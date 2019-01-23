from cis_interface import backwards
from cis_interface.serialize.tests import test_DefaultSerialize as parent


class TestAsciiMapSerialize(parent.TestDefaultSerialize):
    r"""Test class for TestAsciiMapSerialize class."""

    def __init__(self, *args, **kwargs):
        super(TestAsciiMapSerialize, self).__init__(*args, **kwargs)
        self._cls = 'AsciiMapSerialize'

    def test_error_delim(self):
        r"""Test error for message with too many delimiters on a line."""
        msg = backwards.as_bytes(self.instance.delimiter.join(
            ['args1', 'val1', 'args2', 'val2']))
        self.assert_raises(ValueError, self.instance.deserialize, msg)

    def test_error_nonstrval(self):
        r"""Test error on serializing dictionary with non-string values."""
        obj = {1: 'here'}
        self.assert_raises(ValueError, self.instance.serialize, obj)

    def test_remove_quotes(self):
        r"""Test deserialization of message with single quotes."""
        send_msg = b"a\t'a_value'\n"
        recv_msg = {'a': 'a_value'}
        self.assert_equal(self.instance.deserialize(send_msg)[0], recv_msg)
