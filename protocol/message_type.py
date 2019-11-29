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
    #add_friend = 4
    #resolve_friend_request = 5

    # {target_type:int(0=私聊 1=群聊),target_id:int,message:str}
    send_message = 6

    # id:int
    join_room = 7
    # name:str
    create_room = 8
    # id:int
    query_room_users = 9

    bad = 10

    # === Server Action 101-200
    login_successful = 100
    register_successful = 101
    #incoming_friend_request = 102
    contact_info = 103
    chat_history = 104
    server_echo = 105
    # [successful:bool,err_msg:str]
    #add_friend_result = 106
    # [online:bool,friend_user_id:int]
    #friend_on_off_line = 107
    notify_chat_history = 108
    # [target_type:int(0=私聊 1=群聊),target_id:int,message:str,sender_id:int,sender_name:str,time:int]
    on_new_message = 109
    server_kick = 110
    query_room_users_result = 111
    # [room_id, user_id, online]
    room_user_on_off_line = 112
    login_bundle = 113

    # === Failure 201-300
    login_failed = 201
    username_taken = 202
    # err_msg:str
    general_failure = 203
    # msg:str
    general_msg = 204


def _get_message_type_from_value(value):
    return MessageType(value)