import enum

class MessageType(enum.IntEnum):
    """里面规定了各个信息类型对应的标号以及处理指令对应的标号"""
    # === Client Action 1-100
    # [username, password]
    login = 1
    # [username, password]
    register = 2
    require_list = 3
    download = 4
    start_read = 5
    pre_page = 6
    nxt_page = 7
    view_comment = 8
    comment = 9
    bad = 10

    # === Server Action 101-200
    login_successful = 101
    register_successful = 102
    book_list = 103
    file_size = 104
    send_page = 105

    # === Failure 201-300
    login_failed = 201
    username_taken = 202
    no_more_page = 203 # 当前页是最后一页
    send_failed = 204
    # err_msg:str
    general_failure = 205
    # msg:str
    general_msg = 206


def _get_message_type_from_value(value):
    return MessageType(value)