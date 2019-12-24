import os
import math
from protocol.message_type import MessageType
from protocol.secure_transmission.secure_channel import SecureChannel
from server.memory import *
from server.event.utils import ONE_PAGE_WORDS, get_chapter, send_page

def run(sc, parameters):
    """
    发送流程：
        当前所处页数
        当前所处章数
        总页数
        总章数
        页面
    """
    info = parameters.split('*')
    user_name = info[0] # 用户名
    bkname = info[1] # 书名

    # 检查该书是否在服务器中
    bklist = os.listdir('./server/books')
    for i in range(len(bklist)):
        bklist[i] = bklist[i].strip('.txt')
    if bkname not in bklist: # 如果这本书不在书籍列表里
        sc.send_message(MessageType.no_book)
        return

    # 查找书签
    page_num = 0 # 初始化书签为0
    with open('./server/users.txt', 'r', encoding='utf-8') as f:
        users = f.read().splitlines() # 转化为列表
        for user in users:
            user = user.split('|')
            if user[0] == user_name: # 找到该用户
                index = user.index(bkname) if (bkname in user) else -1
                if index != -1: # 找到该书的书签
                    page_num = int(user[index+1])
                break
    sc.send_message(MessageType.page_num, page_num) # 将书签所在页数发送给客户端
    
    # 当前章节
    chap = get_chapter('./server/books/' + bkname + '.txt', page_num)
    sc.send_message(MessageType.send_chapter, chap) # 发送书签所在章数

    # 计算总页数和总章数
    total_page = 0
    total_chap = 0
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
            total_page += math.ceil(len(s) / ONE_PAGE_WORDS)
            total_chap += 1
    sc.send_message(MessageType.total_page, total_page-1) # 发送总页数
    sc.send_message(MessageType.total_chap, total_chap-1) # 发送总章数

    # 发送书签页
    send_page(sc, './server/books/' + bkname + '.txt', page_num)

    return