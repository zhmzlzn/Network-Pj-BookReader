import select
import _tkinter
import tkinter as tk
from tkinter import messagebox
from tkinter import *
from protocol.secure_transmission.secure_channel import establish_secure_channel_to_server
from protocol.message_type import MessageType
from protocol.data_conversion.from_byte import deserialize_message
from client.memory import current_user
import client.memory

class RegisterForm(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.createForm()
        self.sc = client.memory.sc
        master.protocol("WM_DELETE_WINDOW", self.remove_socket_listener_and_close)    

    def createForm(self):
        self.master.resizable(width=False, height=False)
        self.master.geometry('300x140')
        self.master.title("Jack的阅读器-注册")

        self.label_1 = Label(self, text="用户名")
        self.label_2 = Label(self, text="密码")
        self.label_3 = Label(self, text="确认密码")

        self.username = Entry(self)
        self.password = Entry(self, show="*")
        self.password_confirmation = Entry(self, show="*")

        self.label_1.grid(row=0, sticky=E)
        self.label_2.grid(row=1, sticky=E)
        self.label_3.grid(row=2, sticky=E)

        self.username.grid(row=0, column=1, pady=(10, 6))
        self.password.grid(row=1, column=1, pady=(0, 6))
        self.password_confirmation.grid(row=2, column=1, pady=(0, 6))

        self.regbtn = Button(self, text="注册", command=self.do_register)
        self.regbtn.grid(row=4, column=0, columnspan=2)

        self.pack()

    def do_register(self):
        username = self.username.get()
        password = self.password.get()
        password_confirmation = self.password_confirmation.get()
        if not username:
            messagebox.showerror("出错了", "用户名不能为空")
            return
        if not password:
            messagebox.showerror("出错了", "密码不能为空")
            return
        if password != password_confirmation:
            messagebox.showerror("出错了", "两次密码输入不一致")
            return

        self.sc.send_message(MessageType.register, [username, password])
        # 接收服务器反馈
        message = self.sc.recv_message()
        if not message:
            messagebox.showerror('连接失败', 'QAQ 网络出现了问题，请稍后再试~')
            return

        if message['type'] == MessageType.username_taken:
            messagebox.showerror('出错了', '用户名已被使用，请换一个')
            return

        if message['type'] == MessageType.register_successful:
            messagebox.showinfo('注册成功', '恭喜，注册成功！')
            self.master.destroy()
            return
