"""
1. 定义了SecureChannel和其可以实现的操作，所有的信息发送都应该调用其中的函数
2. 定义了服务器和客户端建立SecureChannel的函数
"""

import math
import os
import socket
import struct

from Crypto.Cipher import AES # AES为加密算法

from protocol.utils.read_config import get_config # 读取config.json的内容
from protocol.secure import cryptogram # 加载密码生成文件
'''from common.message import serialize_message, deserialize_message, ByteArrayReader'''
from protocol.util import long_to_bytes
from pprint import pprint


# Format of message transmitted through Secure Channel
# |--Length of Message Body(4Bytes)--|--Length of AES padding (1Byte)--|--AES IV (16Bytes)--|--Message Body (CSON)--|

class SecureChannel:
    """下面定义了secure channel建立后可以提供的操作"""
    def __init__(self, socket, shared_secret):
        socket.setblocking(False) # 参数为False表示设置socket为非阻塞方式，不会等待信息
        self.socket = socket
        self.shared_secret = shared_secret
        return

    def send(self, message_type, parameters=None):
        """加密message_type的数据parameters并发送"""
        iv1 = bytes(os.urandom(16)) # 有os随机生成一个byte格式的Initialization Vector(IV)
        data_to_encrypt = serialize_message(message_type, parameters) # 将各个类型的数据按照规定的转化格式转化为bytes
        length_of_message = len(data_to_encrypt) # 转化为byte后的长度
        padding_n = math.ceil(length_of_message / 16) * 16 - length_of_message # ceil向上取整；计算需要填补的空位数
        for i in range(0, padding_n):
            data_to_encrypt += b'\0'

        encryption_suite = AES.new(self.shared_secret, AES.MODE_CBC, iv1) # AES.CBC加密器
        encrypted_message = encryption_suite.encrypt(data_to_encrypt) # 加密
        length_of_encrypted_message = len(encrypted_message) # 加密后总大小

        # pprint([length_of_encrypted_message,
        #         struct.pack('L', length_of_encrypted_message), bytes([padding_n]), iv1, encrypted_message])
        # pprint(['sending', self.socket, message_type, parameters])

        # 这里最终还是用socket发送，但是还是封装了一个头部，并且后面的主要信息（encrypted_message）已被加密
        self.socket.send(
            struct.pack('!L', length_of_encrypted_message) + bytes([padding_n]) + iv1 + encrypted_message)
            # 👆 pack格式：!L + 信息长度 + padding长度 + IV + 信息
        return

    def on_data(self, data_array):
        """数据解密，即解密收到的data_array"""
        # 用select循环socket.recv，当收到一个完整的数据块后（收到后length_of_encrypted_message+1+16个字节后）
        # 把 bytes([padding_n]) + iv1 + encrypted_message 传给本函数
        br = ByteArrayReader(data_array)

        # pprint(['recv', 'first_4_bytes', first_4_bytes, length_of_encrypted_message])
        padding_n = br.read(1)[0] # 解读出补位数
        # pprint(['recv', 'padding_n', padding_n])

        iv = br.read(16) # 读出IV（解密需要的部分）
        # pprint(['recv', 'iv', iv])
        # incomplete
        bytes_received = 0
        data = br.read_to_end()

        decryption_suite = AES.new(self.shared_secret, AES.MODE_CBC, iv) # AES.CBC解密器
        decrypted_data = decryption_suite.decrypt(data) # 解密

        if padding_n != 0:
            decrypted_data = decrypted_data[0:-padding_n] # 扔掉补为的部分
        # pprint(['recv', 'decrypted_data', decrypted_data])

        return deserialize_message(decrypted_data)

    def close(self):
        """关闭socket"""
        self.socket.close()


def establish_secure_channel_to_server():
    """客户端建立安全通道"""
    config = get_config() # config里面存放了密钥和连接的地址，端口
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.connect((config['client']['server_ip'], int(config['client']['server_port']))) # 建立连接

    # 首次连接，发送客户端自己的密钥
    s.send(long_to_bytes(crypt.my_secret))

    # 首次连接，接受服务器发来的密钥
    data = s.recv(1024)
    their_secret = int.from_bytes(data, byteorder='big')

    # 计算出共同密钥
    shared_secret = crypt.get_shared_secret(their_secret)

    sc = SecureChannel(s, shared_secret)

    return sc


def accept_client_to_secure_channel(socket):
    """服务器建立安全通道"""
    conn, addr = socket.accept() # 这里仍然使用socket接收

    # 首次连接，接收客户端发来的密钥
    data = conn.recv(1024)
    their_secret = int.from_bytes(data, byteorder='big') # 将byte转化为int

    # 首次连接，发送服务器自己的密钥
    conn.send(long_to_bytes(crypt.my_secret)) # int转化为byte才发送

    # 计算出共同密钥
    shared_secert = crypt.get_shared_secret(their_secret)

    sc = SecureChannel(conn, shared_secert)

    return sc
