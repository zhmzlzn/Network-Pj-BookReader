import tkinter as tk
from tkinter import *
from tkinter import messagebox
from protocol.secure_transmission.secure_channel import establish_secure_channel_to_server
import client.memory
from client.forms.login_form import LoginForm

def init_client():
    """启动客户端"""
    root = tk.Tk() # 建立一个窗口，名为root
    client.memory.tk_root = root 

    try:
        client.memory.sc = establish_secure_channel_to_server() # 建立一条到服务器的安全连接

    except ConnectionError:
        messagebox.showerror("出错了", "无法连接到服务器")
        exit(1)

    login = tk.Toplevel(root) # 建立顶级独立窗口
    LoginForm(master=login)

    root.withdraw()
    root.mainloop()
    try:
        root.destroy()
    except tk.TclError:
        pass
