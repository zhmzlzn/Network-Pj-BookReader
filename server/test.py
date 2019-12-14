import os

with open('./server/users.txt', 'a+', encoding='utf-8') as f:
    f.write('张飞 123456'+'\n')
    f.write('诸葛亮 123456')

'''
    for line in f.readlines():
        line = line.strip()
        print(line)
        print(type(line))
'''
