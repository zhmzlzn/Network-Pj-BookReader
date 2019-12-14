import _tkinter
import tkinter as tk
from tkinter import messagebox
from protocol.message_type import MessageType
import _thread
from tkinter import *
from tkinter import Toplevel
from protocol.secure_transmission.secure_channel import SecureChannel
from protocol.data_conversion.from_byte import *
import client.memory
from client.forms.register_form import RegisterForm
from client.forms.bookshelf_form import BookshelfForm

class LoginForm(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.createForm()
        self.sc = client.memory.sc

    def createForm(self):
        self.master.resizable(width=False, height=False)
        self.master.geometry('300x100')        
        self.master.title("Jack的阅读器")

        self.label_1 = Label(self, text="用户名")
        self.label_2 = Label(self, text="密码")

        self.username = Entry(self)
        self.password = Entry(self, show="*")

        self.label_1.grid(row=0, sticky=E)
        self.label_2.grid(row=1, sticky=E)

        self.username.grid(row=0, column=1, pady=(10, 6))
        self.password.grid(row=1, column=1, pady=(0, 6))

        self.buttonframe = Frame(self)
        self.buttonframe.grid(row=2, column=0, columnspan=2, pady=(4, 6))

        self.logbtn = Button(self.buttonframe, text="登陆", command=self.do_login)
        self.logbtn.grid(row=0, column=0)

        self.registerbtn = Button(self.buttonframe, text="注册", command=self.show_register)
        self.registerbtn.grid(row=0, column=1)

        self.pack()

    def do_login(self):
        """使用账号和密码登陆"""
        username = self.username.get()
        password = self.password.get()
        if not username:
            messagebox.showerror("出错了！", "用户名不能为空")
            return
        if not password:
            messagebox.showerror("出错了！", "密码不能为空")
            return

        # 发送登陆消息
        self.sc.send_message(MessageType.login, [username, password])
        print('已发送请求登陆的消息')

        # 接收服务器反馈
        #message = self.sc.socket.recv(1024)
        message = self.sc.client_recv()
        if not message:
            messagebox.showerror('连接失败', 'QAQ 网络出现了问题，请稍后再试~')
            self.destroy_window()
            return

        """处理点击登陆收到的信息"""
        # 登陆失败
        if message['type'] == MessageType.login_failed:
            messagebox.showerror('登陆失败', '用户名或密码错误！')
            return

        # 登陆成功
        if message['type'] == MessageType.login_successful:
            client.memory.current_user = username 
            print('登陆成功')
            # 打开书架窗口（书籍列表）
            bookshelf = Toplevel(client.memory.tk_root, takefocus=True)
            BookshelfForm(bookshelf)

            return

    def show_register(self):
        register_form = Toplevel()
        RegisterForm(register_form)

    def destroy_window(self):
        client.memory.tk_root.destroy()