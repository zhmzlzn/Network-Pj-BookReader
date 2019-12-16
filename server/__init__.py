"""
初始化服务器，等待客户端请求
"""
import socket
import struct
import sys
import traceback
import select

from protocol.utils.read_config import get_config
from protocol.secure_transmission.secure_channel import accept_client_to_secure_channel
from protocol.data_conversion.from_byte import deserialize_message
from protocol.message_type import MessageType

from server.event import handle_event
from server.memory import *
import server.memory

from pprint import pprint

def init_server():
    """
    初始化服务器，等待客户端请求
    收到客户端的信息，首先进行类别判断，然后调用对应的函数进行响应
    """
    config = get_config()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 👇 level=通用套接字，选项：允许重用本地地址和端口
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    s.bind((config['server']['bind_ip'], config['server']['bind_port']))
    s.listen(3)

    print("Server listening on " + config['server']['bind_ip'] + ":" + str(config['server']['bind_port']))

    # 三个字典
    bytes_to_receive = {} # 要接收的包
    bytes_received = {} # 已接收的包
    data_buffer = {}

    while True:
        # 👇 接收并监控3个通信列表，第一个是所有的输入的data,就是指外部发过来的数据，第2个是监控和接收所有要发出去的data,第3个监控错误信息
        rlist, wlist, xlist = select.select(list(map(lambda x: x.socket, scs)) + [s], [], [])

        for i in rlist:

            if i == s:
                # 监听socket为readable，说明有新的客户要连入
                sc = accept_client_to_secure_channel(s) # 用该socket建立安全通道
                socket_to_sc[sc.socket] = sc
                scs.append(sc)
                bytes_to_receive[sc] = 0
                bytes_received[sc] = 0
                data_buffer[sc] = bytes()
                continue

            # 如果不是监听socket，就是旧的客户发消息过来了
            sc = socket_to_sc[i]

            if bytes_to_receive[sc] == 0 and bytes_received[sc] == 0:
                # 一次新的接收
                conn_ok = True
                first_4_bytes = ''
                try:
                    first_4_bytes = sc.socket.recv(4) # 接收4bytes，内容是message的长度
                except ConnectionError:
                    conn_ok = False

                if first_4_bytes == "" or len(first_4_bytes) < 4:
                    conn_ok = False

                if not conn_ok:
                    sc.close()
                    # 把他的连接信息移除
                    remove_sc_from_socket_mapping(sc)

                else:
                    data_buffer[sc] = bytes()
                    # 要接收的长度为
                    bytes_to_receive[sc] = struct.unpack('!L', first_4_bytes)[0]
            buffer = sc.socket.recv(bytes_to_receive[sc] - bytes_received[sc])
            data_buffer[sc] += buffer # 接收后放到buffer里
            bytes_received[sc] += len(buffer)

            if bytes_received[sc] == bytes_to_receive[sc] and bytes_received[sc] != 0:
                # 当一个数据包接收完毕
                bytes_to_receive[sc] = 0
                bytes_received[sc] = 0
                try:
                    data = sc.decrypt_data(data_buffer[sc])
                    message = deserialize_message(data)
                    # 这里我们得到了一个来自客户端的请求，现在需要判断是什么请求来调用相应的函数相应
                    # 调用event文件夹__init__.py文件中的函数，识别message_type并调用对应的函数
                    handle_event(sc, message['type'], message['parameters'])
                except:
                    pprint(sys.exc_info())
                    traceback.print_exc(file=sys.stdout)
                    pass
                data_buffer[sc] = bytes()
