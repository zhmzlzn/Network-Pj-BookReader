import os
from protocol.message_type import MessageType
from protocol.secure_transmission.secure_channel import SecureChannel
from server.memory import *

def run(sc, parameters):
    info = parameters.split('*')
    user_name = info[0] # 用户名
    bkname = info[1] # 书名
    n = info[2] # 页数

    # 检查该书是否在服务器中
    bklist = os.listdir('./server/books')
    for i in range(len(bklist)):
        bklist[i] = bklist[i].strip('.txt')
    if bkname not in bklist: # 如果这本书不在书籍列表里
        print('错误！没有找到这本书！')
        return

    # 修改书签
    with open('./server/users.txt', 'r', encoding='utf-8') as f:
        users = f.read().splitlines() # 转化为列表
        for i in range(len(users)):
            user_lst = users[i].split('|')
            if user_lst[0] == user_name: # 找到该用户
                index = user_lst.index(bkname) if (bkname in user_lst) else -1
                if index == -1: # 这本书没有记录，加到最后
                    users[i] = users[i] + '|' + bkname + '|' + str(n)
                else:
                    user_lst[index+1] = str(n)
                    users[i] = '|'.join(user_lst)
                break
    with open('./server/users.txt', 'w', encoding='utf-8') as f:
        users = '\n'.join(users) + '\n'
        f.write(users)

    return