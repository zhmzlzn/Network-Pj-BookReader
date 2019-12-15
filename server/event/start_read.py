import os
from protocol.message_type import MessageType
from protocol.secure_transmission.secure_channel import SecureChannel
from server.memory import *

def run(sc, parameters):
    bkname = parameters # 书名
    bklist = os.listdir('./server/books')
    for i in range(len(bklist)):
        bklist[i] = bklist[i].strip('.txt')
    if bkname not in bklist: # 如果这本书不在书籍列表里
        print('错误！没有找到这本书！')
        return

    with open('./server/books/' + bkname + '.txt', 'rb') as f: # 以二进制只读模式打开
        '''
        实现书签启用
        for i in range(n):
            filedata = f.read(992)
        filedata = f.read(992)
        if not filedata:
            sc.send_message(MessageType.no_more_page)
        '''
        filedata = f.read(1900)
        sc.send_page(filedata)
    return