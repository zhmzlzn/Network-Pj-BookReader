import os
import math
from protocol.message_type import MessageType
from protocol.secure_transmission.secure_channel import SecureChannel
from server.memory import *
from server.event.utils import ONE_PAGE_WORDS, send_page

def run(sc, parameters):
    info = parameters.split('*')
    bkname = info[0] # 书名
    chap = int(info[1]) # 章数
    bklist = os.listdir('./server/books')
    for i in range(len(bklist)):
        bklist[i] = bklist[i].strip('.txt')
    if bkname not in bklist: # 如果这本书不在书籍列表里
        sc.send_message(MessageType.no_book)
        return

    old_page = 0
    new_page = 0
    chapter = -1
    with open('./server/books/' + bkname + '.txt', 'r', encoding='utf-8') as f:
        line = f.readline()
        while line:
            s = ''
            s += line
            line = f.readline()
            while line:
                if line[0] == '#':
                    break
                s += line
                line = f.readline()
            old_page = new_page
            new_page += math.ceil(len(s) / ONE_PAGE_WORDS)
            chapter += 1
            if chapter == chap:
                break
        sc.send_message(MessageType.page_num, old_page)
        send_page(sc, './server/books/' + bkname + '.txt', old_page)
    return