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
from protocol.secure_transmission import cryptogram # 加载密码生成文件
from protocol.utils import long_to_bytes
from protocol.data_conversion.from_byte import *
from protocol.data_conversion.to_byte import serialize_message
from protocol.message_type import MessageType


# Format of message transmitted through Secure Channel
# |--Length of Message Body(4Bytes)--|--Length of AES padding (1Byte)--|--AES IV (16Bytes)--|--Message Body (CSON)--|

class SecureChannel:
    """
    下面定义了secure channel建立后可以提供的操作。
    作为最高层次的封装，其应该提供发送（原数据加密+socket发送）和接收（socket接收+数据解密）；
    其提供的发送和接收应该取代socket的发送和接收，应该和下面的封装没有牵扯。
    args: 
        socket 用于传输
        shared_secret 安全通道的共享密钥
    """
    def __init__(self, socket, shared_secret):
        #socket.setblocking(False) # 参数为False表示设置socket为非阻塞方式，不会等待信息
        self.socket = socket
        self.shared_secret = shared_secret
        return

    def encrypt_data(self, message):
        """加密数据"""
        iv = bytes(os.urandom(16)) # 有os随机生成一个byte格式的Initialization Vector(IV)
        # 这里默认发送的一条数据应当是由 数据类型开头 + 数据本身 组成
        length_of_message = len(message) # 转化为byte后的长度
        padding_n = math.ceil(length_of_message / 16) * 16 - length_of_message # ceil向上取整；计算需要填补的空位数
        for i in range(0, padding_n):
            message += b'\0'

        encryption_suite = AES.new(self.shared_secret, AES.MODE_CBC, iv) # AES.CBC加密器
        encrypted_message = encryption_suite.encrypt(message) # 加密
        #length_of_encrypted_message = len(encrypted_message) # 加密后总大小

        return bytes([padding_n]) + iv + encrypted_message
            # 👆 pack格式：padding长度 + IV + 信息

    def decrypt_data(self, data_array):
        """
        数据解密，即解密收到的data_array
        此时data_array应包含 padding + iv + encrypted_message
        """
        # 用select循环socket.recv，当收到一个完整的数据块后（收到后length_of_encrypted_message+1+16个字节后）
        # 把 bytes([padding_n]) + iv + encrypted_message 传给本函数
        br = ByteArrayReader(data_array) # 定义一个byte解读器

        padding_n = br.read(1)[0] # 解读出补位数

        iv = br.read(16) # 读出IV（解密需要的部分）
        bytes_received = 0
        data = br.read_to_end()

        decryption_suite = AES.new(self.shared_secret, AES.MODE_CBC, iv) # AES.CBC解密器
        decrypted_data = decryption_suite.decrypt(data) # 解密

        if padding_n != 0:
            decrypted_data = decrypted_data[0:-padding_n] # 扔掉补为的部分

        return decrypted_data

    def send_message(self, message_type, parameters=None):
        """
        发送message类消息
        转化为bytes 👉 调用encrypt_data函数加密 👉 计算出总长度，加到信息最前面 👉 发送
        """
        data_to_encrypt = serialize_message(message_type, parameters)
        encrypted_message = self.encrypt_data(data_to_encrypt)
        length_of_encrypted_message = len(encrypted_message)
        self.socket.send(struct.pack('!L', length_of_encrypted_message) + encrypted_message)  
        return

    def recv_message(self):
        """
        客户端接收message类消息
        识别长度，完全接收 👉 调用decrypt_data函数解密 👉 从bytes转化为原来的类型 👉 返回结果
        """
        bytes_to_receive = 0
        bytes_received = 0
        while True:
            if bytes_to_receive == 0 and bytes_received == 0:
                conn_ok = True
                first_4_bytes = ''
                try:
                    first_4_bytes = self.socket.recv(4) # 接收4bytes，内容是message的长度
                except ConnectionError:
                    conn_ok = False
                if first_4_bytes == "" or len(first_4_bytes) < 4:
                    conn_ok = False
                if not conn_ok:
                    print('连接失败！')
                    return False
                data_buffer = bytes()
                bytes_to_receive = struct.unpack('!L', first_4_bytes)[0]

            buffer = self.socket.recv(bytes_to_receive - bytes_received)
            data_buffer += buffer
            bytes_received += len(buffer)

            if bytes_received == bytes_to_receive:
                data = self.decrypt_data(data_buffer)        
                message = deserialize_message(data)
                return message

    def send_file(self, file_path):
        """服务器加密发送客户端请求的文件"""
        # 传输分为两个部分，先传输文件大小，再传输文件的内容
        self.send_message(MessageType.file_size, os.stat(file_path).st_size)
        
        with open(file_path,'rb') as f: # 以二进制只读模式打开
            while True:
                filedata = f.read(992) # 992 + 16 + 1 = 1009
                if not filedata:
                    break
                encrypted_message = self.encrypt_data(filedata) # 加密，加密后大小为1024
                self.socket.send(encrypted_message)
        
        print('已发送文件')
        return

    def recv_file(self, file_path):
        """客户端从服务器获得名为filename的文件"""
        message = self.recv_message()
        if message['type'] == MessageType.no_book:
            print('查无此书！')
            return
        if message['type'] is not MessageType.file_size:
            print('未能获取文件大小，传输失败！')
            return
        
        filesize = message['parameters'] # 要传输的文件大小
        try:
            with open(file_path,'wb') as f: # 二进制打开文件用于写入
                ressize = filesize # 剩下要接收的大小
                while True:
                    if ressize > 992:
                        buffer = self.socket.recv(1009)
                        filedata = self.decrypt_data(buffer)
                    else:
                        buffer = self.socket.recv((math.ceil(ressize / 16) * 16) + 16 + 1)
                        filedata = self.decrypt_data(buffer)
                        f.write(filedata)
                        break
                    if not filedata:
                        break
                    f.write(filedata)
                    ressize = ressize - len(filedata)
                    if ressize <0:
                        break
            print ('文件传输成功!')
        except Exception as e:
            print (e)
            print ('文件传输失败!')
        return

    def close(self):
        """关闭socket"""
        self.socket.close()


def establish_secure_channel_to_server():
    """
    客户端建立安全通道
    """
    config = get_config() # config里面存放了密钥和连接的地址，端口
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.connect((config['client']['server_ip'], int(config['client']['server_port']))) # 建立连接

    # 首次连接，发送客户端自己的密钥
    s.send(long_to_bytes(cryptogram.my_secret))

    # 首次连接，接受服务器发来的密钥
    data = s.recv(1024)
    their_secret = int.from_bytes(data, byteorder='big')

    # 计算出共同密钥
    shared_secret = cryptogram.get_shared_secret(their_secret)

    sc = SecureChannel(s, shared_secret)
    print('安全通道建立成功')

    return sc


def accept_client_to_secure_channel(socket):
    """
    服务器建立安全通道
    """
    conn, addr = socket.accept() # 这里仍然使用socket接收

    # 首次连接，接收客户端发来的密钥
    data = conn.recv(1024)
    their_secret = int.from_bytes(data, byteorder='big') # 将byte转化为int

    # 首次连接，发送服务器自己的密钥
    conn.send(long_to_bytes(cryptogram.my_secret)) # int转化为byte才发送

    # 计算出共同密钥
    shared_secert = cryptogram.get_shared_secret(their_secret)

    sc = SecureChannel(conn, shared_secert)
    print('安全通道建立成功')

    return sc
