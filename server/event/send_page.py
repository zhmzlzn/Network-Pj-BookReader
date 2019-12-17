import os
from protocol.message_type import MessageType
from protocol.secure_transmission.secure_channel import SecureChannel
from server.memory import *
from server.event.start_read import ONE_PAGE_WORDS

def run(sc, parameters):
    info = parameters.split('*')
    bkname = info[0] # 书名
    n = int(info[1]) # 页数
    bklist = os.listdir('./server/books')
    for i in range(len(bklist)):
        bklist[i] = bklist[i].strip('.txt')
    if bkname not in bklist: # 如果这本书不在书籍列表里
        sc.send_message(MessageType.no_book)
        return

    with open('./server/books/' + bkname + '.txt', 'rb') as f: # 以二进制只读模式打开
        for i in range(n):
            filedata = f.read(ONE_PAGE_WORDS)
        filedata = f.read(ONE_PAGE_WORDS)
        sc.send_page(filedata)
    return