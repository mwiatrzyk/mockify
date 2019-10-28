import struct

import pytest

from mockify import satisfied, ordered
from mockify.actions import Return


class ProtocolReader:

    class ReadError(Exception):
        pass

    def __init__(self, connection):
        self._connection = connection

    def read(self):
        magic_bytes = self._connection.read(3)
        if magic_bytes != b'XYZ':
            raise self.ReadError('Message header is invalid')
        message_length, = struct.unpack('!H', self._connection.read(2))
        message_payload = self._connection.read(message_length)
        return message_payload


class TestProtocolReader:

    @pytest.fixture(autouse=True)
    def setup(self, mock_factory):
        self.connection = mock_factory('connection')
        self.uut = ProtocolReader(self.connection)

    def test_read_fails_if_invalid_magic_bytes_are_received(self):
        self.connection.read.expect_call(3).will_once(Return(b'ABC'))

        with satisfied(self.connection):
            with pytest.raises(ProtocolReader.ReadError) as excinfo:
                self.uut.read()

        assert str(excinfo.value) == 'Message header is invalid'

    def test_read_message_from_connection(self):
        self.connection.read.expect_call(3).will_once(Return(b'XYZ'))
        self.connection.read.expect_call(2).will_once(Return(struct.pack('!H', 13)))
        self.connection.read.expect_call(13).will_once(Return(b'Hello, world!'))

        with satisfied(self.connection):
            with ordered(self.connection):
                assert self.uut.read() == b'Hello, world!'
