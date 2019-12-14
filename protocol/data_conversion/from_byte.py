"""
类型转化函数，将收到封装的byte转化为'int'等类型
"""
import socket
from pprint import pprint

from protocol.utils import long_to_bytes
import enum
from struct import pack, unpack
from protocol.message_type import MessageType

# 每个序列化片段的格式：
# |--VAR_TYPE(1 Byte)--|--DATA_LEN(4 Bytes)--|--DATA--|

# |-- 4 Byte messageType --|-- Array of parameters --|
# for each item in array of params
# |-- 1 Byte Type of params --|-- 4 Bytes Length of body --|-- N Byte Body--|

def _get_message_type_from_value(value):
    return MessageType(value)

VAR_TYPE = {
    1: 'int',
    2: 'float',
    3: 'str',
    4: 'list',
    5: 'dict',
    6: 'bool',
    7: 'bytearray',
}


def _deserialize_int(bytes):
    return int.from_bytes(bytes, 'big')


def _deserialize_bool(value):
    return True if value[0] else False


def _deserialize_float(bytes):
    return unpack('!f', bytes)[0]


def _deserialize_str(bytes):
    return bytes.decode('utf-8')


def _deserialize_bytes(body):
    return bytearray(body)


def _deserialize_list(bytes):
    # |--Body (self-evident length)--|--Body (self-evident length)--|--Body (self-evident length)--|...
    byte_reader = ByteArrayReader(bytes)
    ret = []
    while (not byte_reader.empty()):
        body_type = byte_reader.read(1)[0]
        body = byte_reader.read(int.from_bytes(byte_reader.read(4), byteorder='big'))
        body = _deserialize_by_type[body_type](body)
        ret.append(body)
    return ret


def _deserialize_dict(bytes):
    # |--Length of Key(1Byte)--|--Key--|--Body (self-evident length)--|
    # |--Length of Key(1Byte)--|--Key--|--Body (self-evident length)--|
    # ...
    byte_reader = ByteArrayReader(bytes)
    ret = {}
    while (not byte_reader.empty()):
        len_key = byte_reader.read(1)
        key = byte_reader.read(len_key[0])

        body_type = byte_reader.read(1)[0]
        body = byte_reader.read(int.from_bytes(byte_reader.read(4), byteorder='big'))
        body = _deserialize_by_type[body_type](body)
        ret[key.decode()] = body
    return ret


_deserialize_by_type = [None, _deserialize_int, _deserialize_float, _deserialize_str, _deserialize_list,
                        _deserialize_dict, _deserialize_bool, _deserialize_bytes]


def _deserialize_any(bytes):
    byte_reader = ByteArrayReader(bytes)
    type = byte_reader.read(1)[0]

    if type == 0:
        return None

    body_len = int.from_bytes(byte_reader.read(4), 'big')
    return _deserialize_by_type[type](byte_reader.read(body_len))


def deserialize_message(data):
    ret = {}
    byte_reader = ByteArrayReader(data)
    ret['type'] = _get_message_type_from_value(byte_reader.read(1)[0])

    ret['parameters'] = _deserialize_any(byte_reader.read_to_end())

    return ret

class ByteArrayReader:
    """Byte阅读器"""
    def __init__(self, byte_array):
        self.byte_array = byte_array
        self.pointer = 0

    def read(self, length):
        buffer = self.byte_array[self.pointer: self.pointer + length]
        self.pointer += length
        return buffer

    def read_to_end(self):
        buffer = self.byte_array[self.pointer: len(self.byte_array)]
        self.pointer = len(self.byte_array)
        return buffer

    def empty(self):
        return len(self.byte_array) == self.pointer