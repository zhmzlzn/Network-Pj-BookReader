import enum

class MessageType(enum.IntEnum):
    """里面规定了各个信息类型对应的标号以及处理指令对应的标号"""
    # === Client Action 1-100
    login = 1
    register = 2
    require_list = 3
    download = 4
    start_read = 5
    require_page = 6
    update_bookmark = 7
    view_comment = 8
    comment = 9

    # === Server Action 101-200
    login_successful = 101
    register_successful = 102
    book_list = 103
    file_size = 104
    send_page = 105
    bookmark = 106
    total_page = 107

    # === Failure 201-300
    login_failed = 201 # 登陆失败
    username_taken = 202 # 用户名被占用
    no_book = 203 # 查无此书

def _get_message_type_from_value(value):
    return MessageType(value)