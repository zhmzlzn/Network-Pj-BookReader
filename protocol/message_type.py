import enum

class MessageType(enum.IntEnum):
    """里面规定了各个信息类型对应的标号以及处理指令对应的标号"""
    # === Client Action 1-100
    # [username, password]
    login = 1
    # [username, password]
    register = 2
    client_echo = 3
    # username:str
    require_book = 4    
    require_comment = 5
    comment = 6
    bad = 7

    # === Server Action 101-200
    login_successful = 100
    register_successful = 101
    server_echo = 103
    send_check = 104
    sending_file = 105
    last_send = 106


    # === Failure 201-300
    login_failed = 201
    username_taken = 202
    send_failed = 203
    # err_msg:str
    general_failure = 204
    # msg:str
    general_msg = 205


def _get_message_type_from_value(value):
    return MessageType(value)