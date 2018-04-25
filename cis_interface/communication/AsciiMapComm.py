from cis_interface.communication import FileComm


class AsciiMapComm(FileComm.FileComm):
    r"""Class for handling I/O from/to a ASCII map on disk.

    Args:
        name (str): The environment variable where file path is stored.
        **kwargs: Additional keywords arguments are passed to parent class.

    """
    def __init__(self, name, **kwargs):
        kwargs.setdefault('readmeth', 'read')
        kwargs['serializer_kwargs'] = dict(stype=7)
        super(AsciiMapComm, self).__init__(name, **kwargs)
