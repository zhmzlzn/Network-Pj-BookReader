import enum

class MessageType(enum.IntEnum):
    """里面规定了各个信息类型对应的标号以及处理指令对应的标号"""
    # === Client Action 1-100
    # [username, password]
    login = 1
    # [username, password]
    register = 2
    require_list = 3
    read = 4
    download = 5
    view_comment = 6
    comment = 7
    bad = 8
    client_echo = 9

    # === Server Action 101-200
    login_successful = 101
    register_successful = 102
    book_list = 103
    send_page = 104
    file_size = 105

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