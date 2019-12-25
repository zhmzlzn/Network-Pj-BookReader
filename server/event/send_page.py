import os
from protocol.message_type import MessageType
from protocol.secure_transmission.secure_channel import SecureChannel
from server.memory import *
from server.event.utils import send_page

def run(sc, parameters):
    info = parameters.split('*')
    bkname = info[0] # 书名
    page_num = int(info[1]) # 页数
    bklist = os.listdir('./server/books')
    for i in range(len(bklist)):
        bklist[i] = bklist[i].strip('.txt')
    if bkname not in bklist: # 如果这本书不在书籍列表里
        sc.send_message(MessageType.no_book)
        return

    send_page(sc, './server/books/' + bkname + '.txt', page_num)

    return