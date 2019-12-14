from protocol.message_type import MessageType
from protocol.utils import md5
from protocol.secure_transmission.secure_channel import SecureChannel
from server.memory import *


def run(sc, parameters):
    parameters[0] = parameters[0].strip().lower() # strip：删除开头结尾的字符 lower：把A-Z转化为小写
    with open('./server/users.txt', 'r', encoding='utf-8') as f:
        users = f.read().splitlines()
        for user in users:
            user = user.split(' ')
            if parameters[0] == user[0] and parameters[1] == user[1]: # 用户名和密码正确
                sc.send_message(MessageType.login_successful)
                print('用户名和密码正确，已发送登陆成功消息')
                return

    sc.send_message(MessageType.login_failed)
    return
