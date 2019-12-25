import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter.filedialog import askdirectory # 选择路径
from protocol.secure_transmission.secure_channel import establish_secure_channel_to_server
from protocol.message_type import MessageType
from protocol.data_conversion.from_byte import deserialize_message
from client.forms.reader_form import ReaderForm
from client.memory import current_user
import client.memory

class BookshelfForm(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.sc = client.memory.sc
        self.createForm()        
        master.protocol("WM_DELETE_WINDOW", self.destroy_window)

    def createForm(self):
        self.master.title("Jack的书架")

        self.sb = Scrollbar(self)
        self.sb.pack(side=RIGHT, fill=Y)

        self.booklist = Listbox(self, height=15, width=30, yscrollcommand=self.sb.set)
        bklist = self.get_booklist() # 书籍列表
        for bkname in bklist:
            self.booklist.insert(END, bkname)
        self.booklist.pack(side=RIGHT, fill=BOTH, expand=YES)
        
        self.sb.config(command=self.booklist.yview)

        self.buttonframe = Frame(self)
        self.buttonframe.pack(side=LEFT, fill=BOTH, expand=YES)
        self.refreshbtn = Button(self.buttonframe, text="刷新", command=self.refresh)
        self.refreshbtn.pack(side=TOP, fill=Y, expand=YES)
        self.readbtn = Button(self.buttonframe, text="阅读", command=self.read)
        self.readbtn.pack(side=TOP, fill=Y, expand=YES)
        self.dlbtn = Button(self.buttonframe, text="下载", command=self.download)
        self.dlbtn.pack(side=TOP, fill=Y, expand=YES)

        self.pack()

    def get_booklist(self):
        """
        获得书籍列表
        这里默认所有书籍可以在一条消息的最长限度内传完
        如果书籍太多，可以采用维护一个书籍列表txt文件的方法，这里为了简洁不这么做
        """
        self.sc.send_message(MessageType.require_list) # 发送获得书籍列表请求
        print('请求书籍列表……')
        # 接收服务器反馈
        message = self.sc.recv_message()
        if not message:
            messagebox.showerror('连接失败', 'QAQ 网络出现了问题，请稍后再试~')          
            return
        if message['type'] == MessageType.book_list:
            print('成功接收书籍列表')
            return message['parameters']
        else:
            print('接收书籍列表失败，错误信息{}'.format(message['type']))
            messagebox.showerror('请求失败','请求失败，服务器未返回书籍列表！')
            return

    def refresh(self):
        """刷新书籍列表"""
        self.booklist.delete(0, END)
        bklist = self.get_booklist() # 书籍列表
        for bkname in bklist:
            self.booklist.insert(END, bkname)

    def read(self):
        """选择阅读小说"""
        bkname = self.booklist.get(self.booklist.curselection()) # 得到选择的小说名
        reader = Toplevel(client.memory.tk_root, takefocus=True)
        ReaderForm(bkname, reader)
        return

    def download(self):
        """选择下载小说"""
        path = askdirectory()
        if not path:
            return
        bkname = self.booklist.get(self.booklist.curselection()) # 得到选择的小说名
        self.sc.send_message(MessageType.download, bkname) # 发送下载请求
        print('正在请求下载《{}》……'.format(bkname))        
        self.sc.recv_file(path + '/' + bkname + '.txt') # 若已有同名文件则会覆盖
        messagebox.showinfo('下载成功！','《{}》下载成功！'.format(bkname))
        print('《{}》下载成功！'.format(bkname))
        return

    def destroy_window(self):
        """因为root被withdraw掉了，所以只能通过memory里记住，然后调用这个函数来关掉"""
        client.memory.tk_root.destroy()
