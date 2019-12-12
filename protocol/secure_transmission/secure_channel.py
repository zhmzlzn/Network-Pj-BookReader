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
from protocol.util import long_to_bytes
from protocol.data_conversion.from_byte import ByteArrayReader, deserialize_message
from protocol.data_conversion.to_byte import serialize_message
from pprint import pprint


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
        socket.setblocking(False) # 参数为False表示设置socket为非阻塞方式，不会等待信息
        self.socket = socket
        self.shared_secret = shared_secret
        return

    def send_data(self, message_type, parameters=None):
        """
        加密message_type的数据parameters并发送
        """
        iv = bytes(os.urandom(16)) # 有os随机生成一个byte格式的Initialization Vector(IV)
        # 这里默认发送的一条数据应当是由 数据类型开头 + 数据本身 组成
        data_to_encrypt = serialize_message(message_type, parameters) # 将各个类型的数据按照规定的转化格式转化为bytes
        length_of_message = len(data_to_encrypt) # 转化为byte后的长度
        padding_n = math.ceil(length_of_message / 16) * 16 - length_of_message # ceil向上取整；计算需要填补的空位数
        for i in range(0, padding_n):
            data_to_encrypt += b'\0'

        encryption_suite = AES.new(self.shared_secret, AES.MODE_CBC, iv) # AES.CBC加密器
        encrypted_message = encryption_suite.encrypt(data_to_encrypt) # 加密
        length_of_encrypted_message = len(encrypted_message) # 加密后总大小

        # 这里最终还是用socket发送，但是还是封装了一个头部，并且后面的主要信息（encrypted_message）已被加密
        self.socket.send(
            struct.pack('!L', length_of_encrypted_message) + bytes([padding_n]) + iv + encrypted_message)
            # 👆 pack格式：!L + 信息长度 + padding长度 + IV + 信息
        return

    def receive_data(self, size):
        """
        数据解密，即解密收到的data_array
        arg:
            size 要接收的大小
        ret：
            返回接收到数据转化为的字典，内容为message_type和内容
        """
        data_array = self.socket.recv(size)
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

        return deserialize_message(decrypted_data)

    '''
    def on_data(self, data_array):
        """
        数据解密，即解密收到的data_array
        """
        # 用select循环socket.recv，当收到一个完整的数据块后（收到后length_of_encrypted_message+1+16个字节后）
        # 把 bytes([padding_n]) + iv + encrypted_message 传给本函数
        br = ByteArrayReader(data_array) # 定义一个byte解读器

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
    '''

    def require_file(self, message_type, filename):
        """要求从服务器获得名为filename的文件"""
        send_data(message_type, filename)
        FILEINFO_SIZE = struct.calcsize('????')
        try:
            fhead = on_data(sock.recv(FILEINFO_SIZE))
            filesize = fhead['parameters']
            with open(filename,'wb') as f: # 创建这个文件
                ressize = filesize # 剩下要接收的大小
                while True:
                    if ressize>1024:
                        filedata = on_data(sock.recv(1024))['parameters']
                    else:
                        filedata = on_data(sock.recv(ressize))['parameters']
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

    def send_file(self):
        """加密发送客户端请求的文件"""
        filename = on_data(connect.recv(1024))['parameters'] # 解码得到数据
        #str = message.split('\n')
        files = os.listdir() # files为当前目录下的文件列表
        while True:
            if filename in files: # 如果这个文件在列表里
                break
        # 传输分为两个部分，先传输文件头，再传输文件的内容
        send(file_check, os.stat(filename).st_size)
        
        with open(filename,'rb') as f:
                while True:
                    filedata = f.read(1024)
                    if not filedata:
                        break
                    connect.send(filedata)

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
    s.send(long_to_bytes(crypt.my_secret))

    # 首次连接，接受服务器发来的密钥
    data = s.recv(1024)
    their_secret = int.from_bytes(data, byteorder='big')

    # 计算出共同密钥
    shared_secret = crypt.get_shared_secret(their_secret)

    sc = SecureChannel(s, shared_secret)

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
    conn.send(long_to_bytes(crypt.my_secret)) # int转化为byte才发送

    # 计算出共同密钥
    shared_secert = crypt.get_shared_secret(their_secret)

    sc = SecureChannel(conn, shared_secert)

    return sc
