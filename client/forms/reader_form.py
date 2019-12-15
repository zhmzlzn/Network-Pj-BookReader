import tkinter as tk
from tkinter import *
from protocol.secure_transmission.secure_channel import establish_secure_channel_to_server
from protocol.message_type import MessageType
from protocol.data_conversion.from_byte import deserialize_message
from client.memory import current_user
import client.memory

class ReaderForm(tk.Frame):
    def __init__(self, bkname, master=None):
        super().__init__(master)
        self.master = master
        self.bkname = bkname
        self.sc = client.memory.sc
        self.n = 0 # 当前所在页数
        self.createForm()
        master.protocol("WM_DELETE_WINDOW", self.destroy_window)

    def createForm(self):
        self.master.title("Jack的阅读器")
        #self.master.geometry('400x500')

        # 当前页数
        self.page_label = Label(self, text=str(self.n+1)) 
        self.page_label.pack(side=TOP, fill=NONE, expand=NO)

        self.sb = Scrollbar(self)
        self.sb.pack(side=RIGHT, fill=Y)

        self.text = Text(self)
        self.text.pack(side=TOP, fill=BOTH)
        self.start_read()

        self.sb.config(command=self.text.yview)

        self.buttonframe = Frame(self)
        self.buttonframe.pack(side=BOTTOM, fill=BOTH, expand=YES)
        self.backbtn = Button(self.buttonframe, text="返回", command=self.back)
        self.backbtn.pack(side=LEFT, fill=X, expand=YES)
        self.prebtn = Button(self.buttonframe, text="上一页", command=self.previous_page)
        self.prebtn.pack(side=LEFT, fill=X, expand=YES)
        self.nxtbtn = Button(self.buttonframe, text="下一页", command=self.next_page)
        self.nxtbtn.pack(side=LEFT, fill=X, expand=YES)
        #self.cmtbtn = Button(self.master, text="评论", command=self.make_comment)
        #self.cmtbtn.pack()
        #self.viewcmtbtn = Button(self.master, text="查看评论", command=self.view_comment)
        #self.viewcmtbtn.pack()

        self.pack()

    def start_read(self):
        """请求服务器发送一页"""
        self.sc.send_message(MessageType.start_read, self.bkname)
        message = self.sc.recv_page()
        if not message:
            messagebox.showerror('连接失败', 'QAQ 网络出现了问题，请稍后再试~')   
        elif message['type'] == MessageType.send_page:
            print('成功接收书签页')
            self.text.insert(1.0, message['parameters'])
        else:
            messagebox.showerror('请求失败','请求失败，服务器未返回书签页！')
        return

    def back(self):
        """选择书籍"""

        return

    def previous_page(self):
        """上一页"""
        if self.n == 0:
            messagebox.showwarning('警告！','已经是第一页！')
            return
        self.n = self.n - 1
        # 这里我们需要同时发送书名和当前页数，而send_message只能发送一种类型的数据，所以全部转化为str，用“*”分隔
        self.sc.send_message(MessageType.pre_page, self.bkname + '*' + str(self.n))
        message = self.sc.recv_page()
        if not message:
            messagebox.showerror('连接失败', 'QAQ 网络出现了问题，请稍后再试~')   
        elif message['type'] == MessageType.send_page:
            print('成功接收上一页')
            self.page_label = Label(self, text=str(self.n+1)) # 更新页码
            self.text.delete('1.0', 'end') # 清空text文本框
            self.text.insert(1.0, message['parameters'])
        else:
            messagebox.showerror('请求失败','请求失败，服务器未返回上一页！')
        return

    def next_page(self):
        """下一页"""
        self.n = self.n + 1
        # 这里我们需要同时发送书名和当前页数，而send_message只能发送一种类型的数据，所以全部转化为str，用“*”分隔
        self.sc.send_message(MessageType.nxt_page, self.bkname + '*' + str(self.n))
        message = self.sc.recv_page()
        if not message:
            messagebox.showerror('连接失败', 'QAQ 网络出现了问题，请稍后再试~')   
        elif message['type'] == MessageType.no_more_page:
            messagebox.showwarning('警告！','已经是最后一页！')
        elif message['type'] == MessageType.send_page:
            print('成功接收下一页')
            self.page_label = Label(self, text=str(self.n+1)) # 更新页码
            self.text.delete('1.0', 'end') # 清空text文本框
            self.text.insert(1.0, message['parameters'])
        else:
            messagebox.showerror('请求失败','请求失败，服务器未返回下一页！')
        return

    def destroy_window(self):
        """因为root被withdraw掉了，所以只能通过memory里记住，然后调用这个函数来关掉"""
        client.memory.tk_root.destroy()