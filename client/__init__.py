import _thread # 基本线程和互斥锁支持
import tkinter as tk
from tkinter import messagebox

from protocol.secure_transmission.secure_channel import establish_secure_channel_to_server
from forms.login_form import LoginForm

import client.memory
import client.util.socket_listener
from client.forms.login_form import LoginForm

def init_client():
    """启动客户端"""
    root = tk.Tk() # 建立一个窗口，名为root
    client.memory.tk_root = root 

    try:
        client.memory.sc = establish_secure_channel_to_server() # 建立一条到服务器的安全连接

    except ConnectionError:
        messagebox.showerror("出错了QAQ", "无法连接到服务器")
        exit(1)

    # 建立新线程来执行socket_listener_thread函数，后面为给这个函数的参数
    #_thread.start_new_thread(client.util.socket_listener.socket_listener_thread, (client.memory.sc, root))

    login = tk.Toplevel() # 建立顶级独立窗口
    LoginForm(master=login) 

    root.withdraw()
    root.mainloop()
    try:
        root.destroy()
    except tk.TclError:
        pass
