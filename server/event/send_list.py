import os
from protocol.message_type import MessageType
from protocol.secure_transmission.secure_channel import SecureChannel
from server.memory import *

def run(sc, parameters):
    bklsit = os.listdir('./server/books')
    for i in range(len(bklsit)):
        bklsit[i] = bklsit[i].strip('.txt')
    sc.send_message(MessageType.book_list, bklsit)
    print('已发送书籍列表')
    return