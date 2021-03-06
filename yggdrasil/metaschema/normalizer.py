# Normalizer adapated from the jsonschema validator
import copy
import contextlib
import jsonschema
from yggdrasil.metaschema.datatypes import get_type_class, _jsonschema_ver_maj


class UndefinedProperty(object):
    r"""Class to be used as a flag for undefined properties."""
    pass


class UninitializedNormalized(object):
    r"""Class to be used as a flag for uninitialized normalized value."""
    pass


def create(*args, **kwargs):
    r"""Dynamically create a validation/normalization class that subclasses
    the jsonschema validation class.

    Args:
        normalizers (dict, optional): Keys are tuples representing paths that
            exist within the schema at which the normalization functions stored
            in lists as their value counterparts should be executed. Defaults to
            empty dictionary.
        no_defaults (bool, optional): If True, defaults will not be set during
            normalization. Defaults to False.
        required_defaults (bool, optional): If True, defaults will be set for
            required properties, even if no_defaults is True. Defaults to False.
        *args: Additional arguments are passed to jsonschema.validators.create.
        **kwargs: Additional keyword arguments are passed to
            jsonschema.validators.create.
        
    """
    normalizers = kwargs.pop('normalizers', ())
    no_defaults = kwargs.pop('no_defaults', ())
    required_defaults = kwargs.pop('required_defaults', ())
    validator_class = jsonschema.validators.create(*args, **kwargs)

    class Normalizer(validator_class):
        r"""Class that can be used to normalize (or validate) objects against
        JSON schemas.

        Args:
            *args: Additional arguments are passed to the base validator class.
            **kwargs: Additional keyword arguments are passed to the base
                validator class.

        Attributes:
            NORMALIZERS (dict): Keys are tuples representing paths that exist
                within the schema at which the normalization functions stored in
                lists as their value counterparts should be executed.
            NO_DEFAULTS (bool): If True, defaults will not be set during
                normalization.
            REQUIRED_DEFAULTS (bool): If True, defaults will be set for required
                properties, even if NO_DEFAULTS is True.

        """
        NORMALIZERS = dict(normalizers)
        NO_DEFAULTS = no_defaults
        REQUIRED_DEFAULTS = required_defaults

        def __init__(self, *args, **kwargs):
            super(Normalizer, self).__init__(*args, **kwargs)
            self._normalized = UninitializedNormalized()
            self._normalizing = False
            self._old_settings = {}
            self._path_stack = []
            self._schema_path_stack = []
            self._normalized_stack = []

        def iter_errors(self, instance, _schema=None):
            r"""Iterate through all of the errors encountered during validation
            of an instance at the current level or lower against properties in a
            schema.

            Args:
                instance (object): Instance that will be validated.
                _schema (dict, optional): Schema that the instance will be
                    validated against. Defaults to the schema used to initialize
                    the class.

            Yields:
                ValidationError: Errors encountered during validation of the
                    instance.

            """
            if _schema is None:
                _schema = self.schema

            if self._normalizing:

                if isinstance(self._normalized, UninitializedNormalized):
                    self._normalized = copy.deepcopy(instance)
                instance = self._normalized

            if ((self._normalizing
                 and isinstance(_schema, dict) and (u"$ref" not in _schema))):
                # Path based normalization
                try:
                    # print(self.current_schema_path, instance, type(instance), _schema)
                    if self.current_schema_path in self.NORMALIZERS:
                        normalizers = self.NORMALIZERS[self.current_schema_path]
                        for n in normalizers:
                            instance = n(self, None, instance, _schema)
                except BaseException as e:
                    error = jsonschema.ValidationError(str(e))
                    # set details if not already set by the called fn
                    error._set(
                        validator=n,
                        validator_value=None,
                        instance=instance,
                        schema=_schema)
                    yield error
                self._normalized = instance

                # Do defaults for required fields
                if (((((not self.NO_DEFAULTS) or self.REQUIRED_DEFAULTS)
                      and isinstance(_schema.get('required', None), list)
                      and isinstance(_schema.get('properties', None), dict)
                      and self.is_type(self._normalized, "object")))):
                    for k in _schema['required']:
                        if (((k not in _schema['properties'])
                             or (k in self._normalized))):
                            continue
                        default = _schema['properties'][k].get('default', None)
                        self._normalized[k] = default
                    instance = self._normalized

                # Do default and type first so normalization can be validated
                for k in ['default', 'type']:
                    if (((k != 'default')
                         and isinstance(instance, UndefinedProperty))):
                        return
                    if k not in _schema:
                        continue
                    v = _schema[k]
                    validator = self.VALIDATORS.get(k)
                    if validator is None:
                        continue
                    errors = validator(self, v, instance, _schema) or ()
                    for error in errors:
                        # set details if not already set by the called fn
                        error._set(
                            validator=k,
                            validator_value=v,
                            instance=instance,
                            schema=_schema,
                        )
                        if k != u"$ref":
                            error.schema_path.appendleft(k)
                        yield error

                    instance = self._normalized

                self._normalized = instance

            for e in super(Normalizer, self).iter_errors(instance, _schema=_schema):
                yield e

        @property
        def current_path(self):
            r"""tuple: Current path from the top of the instance to the current
            instance being validated/normalized."""
            return tuple(self._path_stack)

        @property
        def current_schema_path(self):
            r"""tuple: Current path from the top of the schema to the current
            schema being used for validation/normalization."""
            return tuple(self._schema_path_stack)

        @contextlib.contextmanager
        def normalizing(self, **kwargs):
            r"""Context for normalization that records normalizers before
            context is initialized so that they can be restored once the context
            exist.

            Args:
                **kwargs: Keyword arguments are treated as attributes that
                    should be added to the class in the context. If the class
                    already has an attribute of the same name, it is stored
                    for restoration after the context exits.

            Yields:
                ValidationError: Errors encountered during validation.

            """
            for k, v in kwargs.items():
                if k == 'normalizers':
                    if self.NORMALIZERS:  # pragma: debug
                        raise Exception("Uncomment lines below to allow "
                                        + "addition of default normalizers.")
                    # for ik, iv in self.NORMALIZERS.items():
                    #     v.setdefault(ik, iv)
                elif k == 'validators':
                    for ik, iv in self.VALIDATORS.items():
                        v.setdefault(ik, iv)
                if hasattr(self, k.upper()):
                    ksub = k.upper()
                else:
                    ksub = k
                self._old_settings[ksub] = getattr(self, ksub, None)
                setattr(self, ksub, v)
            self._normalizing = True
            try:
                yield
            finally:
                for k, v in self._old_settings.items():
                    if v is None:
                        delattr(self, k)
                    else:
                        setattr(self, k, v)
                self._old_settings = {}
                self._normalizing = False

        def descend(self, instance, schema, path=None, schema_path=None):
            r"""Descend along a path in the schema/instance, recording
            information about the normalization state so that it can be replaced
            with the original value if there is a validation error along the
            descent path.

            Args:
                instance (object): Current instance being validated against the
                    schema.
                schema (dict): Current schema that the instance is being
                    validated against.
                path (str, int, optional): Path that resulted in the current
                    instance. Defaults to None.
                schema_path (str, int, optional): Path that resulted in the
                    current schema. Defaults to None.

            Yields:
                ValidationError: Errors raised during validation of the instance.

            """
            if self._normalizing:
                if path is not None:
                    self._normalized_stack.append(self._normalized)
                    self._normalized = UninitializedNormalized()
                else:
                    self._normalized_stack.append(self._normalized)
                    self._normalized = copy.deepcopy(self._normalized)
            if path is not None:
                self._path_stack.append(path)
            if schema_path is not None:
                self._schema_path_stack.append(schema_path)
            failed = False
            try:
                for error in super(Normalizer, self).descend(instance, schema,
                                                             path=path,
                                                             schema_path=schema_path):
                    failed = True
                    yield error
            finally:
                if self._normalizing:
                    old_normalized = self._normalized_stack.pop()
                    if not (failed or isinstance(self._normalized, UndefinedProperty)):
                        if path is not None:
                            old_normalized[path] = self._normalized
                        else:
                            old_normalized = self._normalized
                    self._normalized = old_normalized
                if path is not None:
                    self._path_stack.pop()
                if schema_path is not None:
                    self._schema_path_stack.pop()

        def validate(self, instance, _schema=None, normalize=False, **kwargs):
            r"""Validate an instance against a schema.

            Args:
                instance (object): Object to be validated.
                _schema (dict, optional): Schema by which the instance should be
                    validated. Defaults to None and will be set to the schema
                    used to create the class.
                normalize (bool, optional): If True, the instance will also be
                    normalized as it is validated. Defaults to False.
                **kwargs: Additional keyword arguments are passed to the
                    'normalizing' context if normalize is True, otherwise they
                    are ignored.

            Returns:
                object: Normalized instance if normalize == True.

            """
            if normalize:
                with self.normalizing(**kwargs):
                    super(Normalizer, self).validate(instance, _schema=_schema)
                out = self._normalized
                return out
            else:
                super(Normalizer, self).validate(instance, _schema=_schema)

        def normalize(self, instance, _schema=None, **kwargs):
            r"""Normalize an instance during validation, allowing for aliases,
            defaults, or simple type conversions.

            Args:
                instance (object): Object to be normalized and validated.
                _schema (dict, optional): Schema by which the instance should be
                    normalized and validated. Defaults to None and will be set
                    to the schema used to create the class.
                **kwargs: Additional keyword arguments are passed to the
                    'normalizing' context.

            Returns:
                object: Normalized instance.

            """
            with self.normalizing(**kwargs):
                errors = list(self.iter_errors(instance, _schema=_schema))
                # for e in errors[::-1]:
                #     print(80 * '-')
                #     print(e)
                # print(80 * '-')
            if errors:
                return instance
            else:
                return self._normalized

        def is_type(self, instance, types):
            r"""Determine if an object is an example of the given type.

            Args:
                instance (object): Object to test against to the type.
                type (str, list): Name of single type or a list of types that
                    instance should be tested against.

            Returns:
                bool: True if the instance is of the specified type(s). False
                    otherwise.

            """
            out = super(Normalizer, self).is_type(instance, types)
            if (_jsonschema_ver_maj < 3) and out:
                out = get_type_class(types).validate(instance)
            return out

    return Normalizer
