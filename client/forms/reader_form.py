import select
#import _tkinter
import tkinter as tk
from tkinter import *
from protocol.secure_transmission.secure_channel import establish_secure_channel_to_server
from protocol.message_type import MessageType
from protocol.data_conversion.from_byte import deserialize_message
from client.memory import current_user
import client.memory
from client.components.vertical_scrolled_frame import VerticalScrolledFrame

class ReaderForm(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.sc = client.memory.sc
        self.createForm()
        master.protocol("WM_DELETE_WINDOW", self.destroy_window)

    def createForm(self):
        self.master.title("Jack的阅读器")
        #self.master.geometry('400x500')

        self.sb = Scrollbar(self)
        self.sb.pack(side=RIGHT, fill=Y)

        self.text = Text(self)
        self.text.pack(side=TOP, fill=BOTH)
        self.text.insert(INSERT, 'Good!')
        self.text.insert(INSERT, 'very')
        self.text.insert(END, 'Cool')
        self.text.insert(INSERT, '0')
        
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

    def get_page(self)；
        """请求服务器发送一页"""
        
        return

    def back(self):
        """选择阅读小说"""

        return

    def previous_page(self):
        """选择下载小说"""

        return

    def next_page(self):
        return

    def destroy_window(self):
        """因为root被withdraw掉了，所以只能通过memory里记住，然后调用这个函数来关掉"""
        client.memory.tk_root.destroy()