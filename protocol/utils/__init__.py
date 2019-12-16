from binascii import unhexlify
from hashlib import md5 as _md5

def long_to_bytes(val, endianness='big'):
    """
    将数字转化为byte
    """

    width = val.bit_length()
    width += 8 - ((width % 8) or 8)

    fmt = '%%0%dx' % (width // 4)

    s = b'\x00' if fmt % val == '0' else unhexlify(fmt % val)

    if endianness == 'little':
        s = s[::-1]

    return s


def md5(text):
    """MD5加密算法"""
    m = _md5()
    m.update(text.encode('utf-8'))
    return m.hexdigest()
