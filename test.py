bkname = '老残游记'
n = 11
with open('./server/users.txt', 'r', encoding='utf-8') as f:
    users = f.read().splitlines() # 转化为列表
    for i in range(len(users)):
        user_lst = users[i].split('|')
        if user_lst[0] == '1': # 找到该用户
            index = user_lst.index(bkname) if (bkname in user_lst) else -1
            if index == -1: # 这本书没有记录，加到最后
                users[i] = users[i] + '|' + bkname + '|' + str(n)
            else:
                user_lst[index+1] = str(n)
                users[i] = '|'.join(user_lst)
            print(users[i])
            break
    print(users)
with open('./server/users.txt', 'w', encoding='utf-8') as f:
    users = '\n'.join(users) + '\n'
    f.write(users)