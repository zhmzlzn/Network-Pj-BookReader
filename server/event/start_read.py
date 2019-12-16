import os
from protocol.message_type import MessageType
from protocol.secure_transmission.secure_channel import SecureChannel
from server.memory import *

def run(sc, parameters):
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
    n = 0 # 初始化书签为0
    with open('./server/users.txt', 'r', encoding='utf-8') as f:
        users = f.read().splitlines() # 转化为列表
        for user in users:
            user = user.split('|')
            if user[0] == user_name: # 找到该用户
                index = user.index(bkname) if (bkname in user) else -1
                if index != -1: # 找到该书的书签
                    n = int(user[index+1])
                break

    sc.send_message(MessageType.bookmark, n) # 将书签所在页数发送给客户端

    # 发送书签页
    with open('./server/books/' + bkname + '.txt', 'rb') as f: # 以二进制只读模式打开
        for i in range(n):
            filedata = f.read(1900)
        filedata = f.read(1900)
        sc.send_page(filedata)
    return