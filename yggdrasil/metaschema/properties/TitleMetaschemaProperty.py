from yggdrasil.metaschema.properties import register_metaschema_property
from yggdrasil.metaschema.properties.MetaschemaProperty import MetaschemaProperty


@register_metaschema_property
class TitleMetaschemaProperty(MetaschemaProperty):
    r"""Title property with validation of new properties."""

    name = 'title'
    _replaces_existing = True
    _validate = False
