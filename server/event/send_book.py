import os
from protocol.message_type import MessageType
from protocol.secure_transmission.secure_channel import SecureChannel
from server.memory import *

def run(sc, parameters):
    bklist = os.listdir('./server/books')
    for i in range(len(bklist)):
        bklist[i] = bklist[i].strip('.txt')
    if parameters not in bklist: # 如果这本书不在书籍列表里
        sc.send_message(MessageType.no_book)
        return
    sc.send_file('./server/books/' + parameters + '.txt') # 发送这本书
    return


