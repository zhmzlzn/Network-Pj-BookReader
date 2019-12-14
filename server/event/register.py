from protocol.message_type import MessageType
import server.memory
from protocol.utils import md5

def run(sc, parameters):
    parameters[0] = parameters[0].strip().lower() # strip：删除开头结尾的字符 lower：把A-Z转化为小写
    with open('./server/users.txt', 'r', encoding='utf-8') as f:
        users = f.read().splitlines()
        for user in users:
            user = user.split(' ')
            if parameters[0] == user[0]: # 用户名已被占用
                sc.send(MessageType.username_taken)
                return

    # 用户名未被占用，添加到用户列表最后
    with open('./server/users.txt', 'a+', encoding='utf-8') as f:
        f.write(parameters[0] + ' ' + parameters[1] + '\n')
    sc.send(MessageType.register_successful)
    return
