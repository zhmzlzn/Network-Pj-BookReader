"""
类型转化函数，将'int'等类型封装转化为byte
"""
import socket
from pprint import pprint

from protocol.utils import long_to_bytes
import enum
from struct import pack, unpack
from protocol import message_type

# 每个序列化片段的格式：
# |--VAR_TYPE(1 Byte)--|--DATA_LEN(4 Bytes)--|--DATA--|

# |-- 4 Byte messageType --|-- Array of parameters --|
# for each item in array of params
# |-- 1 Byte Type of params --|-- 4 Bytes Length of body --|-- N Byte Body--|

VAR_TYPE_INVERSE = {
    'int': 1,
    'float': 2,
    'str': 3,
    'list': 4,
    'dict': 5,
    'bool': 6,
    'bytearray': 7
}

def _serialize_int(int):
    body = long_to_bytes(int)
    return bytes([VAR_TYPE_INVERSE['int']]) + pack('!L', len(body)) + body


def _serialize_bool(value):
    body = value
    return bytes([VAR_TYPE_INVERSE['bool']]) + pack('!L', 1) + bytes([1 if value else 0])


def _serialize_float(float):
    body = pack('f', float)
    return bytes([VAR_TYPE_INVERSE['float']]) + pack('!L', len(body)) + body


def _serialize_str(str):
    body = str.encode()
    return bytes([VAR_TYPE_INVERSE['str']]) + pack('!L', len(body)) + body


def _serialize_bytes(body):
    return bytes([VAR_TYPE_INVERSE['bytearray']]) + pack('!L', len(body)) + body


def _serialize_list(list):
    # |--Body (self-evident length)--|--Body (self-evident length)--|--Body (self-evident length)--|...
    body = bytearray()
    for i in range(0, len(list)):
        body += _serialize_any(list[i])
    return bytes([VAR_TYPE_INVERSE['list']]) + pack('!L', len(body)) + body


def _serialize_dict(dict):
    # |--Length of Key(1Byte)--|--Key--|--Body (self-evident length)--|
    # |--Length of Key(1Byte)--|--Key--|--Body (self-evident length)--|
    # ...

    body = bytearray()

    for item_key, value in dict.items():
        item_body = _serialize_any(value)
        key_length = len(item_key)

        body += bytes([key_length])
        body += str.encode(item_key)
        body += item_body

    return bytes([VAR_TYPE_INVERSE['dict']]) + pack('!L', len(body)) + body


_serialize_by_type = [None, _serialize_int, _serialize_float, _serialize_str, _serialize_list, _serialize_dict,
                      _serialize_bool, _serialize_bytes]


def _serialize_any(obj):
    if obj is None:
        return bytearray([0])
    type_byte = VAR_TYPE_INVERSE[type(obj).__name__]
    return _serialize_by_type[type_byte](obj)


def serialize_message(message_type, parameters):
    """将message_type和message本身转化为byte合并返回"""
    result = bytes([message_type.value])
    result += _serialize_any(parameters)
    return result