import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter.simpledialog import askinteger
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
        self.user = client.memory.current_user
        self.sc = client.memory.sc
        self.page_num = 0 # 当前所在页数
        self.total_page = 0 # 当前书的总页数
        self.chapter = 0 # 当前所在的章数
        self.total_chapter = 0 # 当前书的总章数
        self.createForm()
        master.protocol("WM_DELETE_WINDOW", self.update_bookmark)

    def createForm(self):
        self.master.title("Jack的阅读器")

        self.sb = Scrollbar(self)
        self.sb.pack(side=RIGHT, fill=Y)

        self.text = Text(self)
        self.text.pack(side=TOP, fill=BOTH)
        self.start_read()

        self.sb.config(command=self.text.yview)

        self.buttonframe = Frame(self)
        self.buttonframe.pack(side=BOTTOM, fill=BOTH, expand=YES)
        self.prechap = Button(self.buttonframe, text="上一章", command=self.previous_chapter)
        self.prechap.pack(side=LEFT, fill=X, expand=YES)
        self.prepg = Button(self.buttonframe, text="上一页", command=self.previous_page)
        self.prepg.pack(side=LEFT, fill=X, expand=YES)
        self.pagebtn = Button(self.buttonframe, text=str(self.page_num+1) + '/' + str(self.total_page+1), command=self.jump_page)
        self.pagebtn.pack(side=LEFT, fill=X, expand=YES)
        self.nxtpg = Button(self.buttonframe, text="下一页", command=self.next_page)
        self.nxtpg.pack(side=LEFT, fill=X, expand=YES)
        self.nxtchap = Button(self.buttonframe, text="下一章", command=self.next_chapter)
        self.nxtchap.pack(side=LEFT, fill=X, expand=YES)

        self.pack()

    def start_read(self):
        """请求服务器发送书签页"""
        self.sc.send_message(MessageType.start_read, self.user + '*' + self.bkname)
        
        # 接收书签所处页数
        message = self.sc.recv_message()
        if message['type'] == MessageType.page_num:
            self.page_num = message['parameters']
            print('《{}》书签位于第{}页'.format(self.bkname, message['parameters']))
        else:
            print('未能成功接收到书签页数！错误：{}'.format(message['type']))
            return

        # 接收书签所处章数
        message = self.sc.recv_message()
        if message['type'] == MessageType.send_chapter:
            self.chapter = message['parameters']
            print('《{}》书签位于第{}章'.format(self.bkname, message['parameters']))
        else:
            print('未能成功接收到书签页数！错误：{}'.format(message['type']))
            return

        # 接收总页数
        message = self.sc.recv_message()
        if message['type'] == MessageType.total_page:
            self.total_page = message['parameters']
            print('《{}》共{}页'.format(self.bkname, message['parameters']))
        else:
            print('未能成功接收到总页数！错误：{}'.format(message['type']))
            return

        # 接收总章数
        message = self.sc.recv_message()
        if message['type'] == MessageType.total_chap:
            self.total_chapter = message['parameters']
            print('《{}》共{}章'.format(self.bkname, message['parameters']))
        else:
            print('未能成功接收到总页数！错误：{}'.format(message['type']))
            return
        
        #接收书签页
        message = self.sc.recv_message()
        if not message:
            messagebox.showerror('连接失败', 'QAQ 网络出现了问题，请稍后再试~')
        elif message['type'] == MessageType.no_book:
            messagebox.showerror('请求失败', '查无此书，请返回刷新书籍列表！')
        elif message['type'] == MessageType.send_page:
            print('成功接收书签页')
            if message['parameters'][0] == '#':
                message['parameters'] = message['parameters'][1:]
            self.text.insert(1.0, message['parameters'])
        else:
            messagebox.showerror('请求失败','请求失败，服务器未返回书签页！')
        return

    def jump_page(self):
        """跳转到某一页"""
        self.page_num = askinteger('页面跳转', '要跳转的页数', initialvalue=self.page_num+1, maxvalue=self.total_page + 1, minvalue=1) - 1
        self.sc.send_message(MessageType.require_page, self.bkname + '*' + str(self.page_num))
        message = self.sc.recv_message()
        if not message:
            messagebox.showerror('连接失败', 'QAQ 网络出现了问题，请稍后再试~')
        elif message['type'] == MessageType.no_book:
            messagebox.showerror('请求失败', '查无此书，请返回刷新书籍列表！')
        elif message['type'] == MessageType.send_page:
            print('成功接收第{}页'.format(self.page_num))
            self.pagebtn['text'] = str(self.page_num+1) + '/' + str(self.total_page+1) # 更新页码
            self.text.delete('1.0', 'end') # 清空text文本框
            if message['parameters'][0] == '#':
                message['parameters'] = message['parameters'][1:]
            self.text.insert(1.0, message['parameters'])
        else:
            messagebox.showerror('请求失败','请求失败，服务器未返回该页！')
        return

    def previous_page(self):
        """上一页"""
        if self.page_num == 0:
            messagebox.showwarning('警告！','已经是第一页！')
            return
        self.page_num = self.page_num - 1
        # 这里我们需要同时发送书名和当前页数，而send_message只能发送一种类型的数据，所以全部转化为str，用“*”分隔
        self.sc.send_message(MessageType.require_page, self.bkname + '*' + str(self.page_num))
        message = self.sc.recv_message()
        if not message:
            messagebox.showerror('连接失败', 'QAQ 网络出现了问题，请稍后再试~')
        elif message['type'] == MessageType.no_book:
            messagebox.showerror('请求失败', '查无此书，请返回刷新书籍列表！')
        elif message['type'] == MessageType.send_page:
            print('成功接收第{}页'.format(self.page_num))
            self.pagebtn['text'] = str(self.page_num+1) + '/' + str(self.total_page+1) # 更新页码
            self.text.delete('1.0', 'end') # 清空text文本框
            if message['parameters'][0] == '#':
                message['parameters'] = message['parameters'][1:]
            self.text.insert(1.0, message['parameters'])
        else:
            messagebox.showerror('请求失败','请求失败，服务器未返回上一页！')
        return

    def next_page(self):
        """下一页"""
        if self.page_num == self.total_page: # 页数从0开始
            messagebox.showwarning('警告！','已经是最后一页！')
            return     
        self.page_num = self.page_num + 1
        # 这里我们需要同时发送书名和当前页数，而send_message只能发送一种类型的数据，所以全部转化为str，用“*”分隔
        self.sc.send_message(MessageType.require_page, self.bkname + '*' + str(self.page_num))
        message = self.sc.recv_message()
        if not message:
            messagebox.showerror('连接失败', 'QAQ 网络出现了问题，请稍后再试~')
        elif message['type'] == MessageType.no_book:
            messagebox.showerror('请求失败', '查无此书，请返回刷新书籍列表！')  
        elif message['type'] == MessageType.send_page:
            print('成功接收第{}页'.format(self.page_num))
            self.pagebtn['text'] = str(self.page_num+1) + '/' + str(self.total_page+1) # 更新页码
            self.text.delete('1.0', 'end') # 清空text文本框
            if message['parameters'][0] == '#':
                message['parameters'] = message['parameters'][1:]
            self.text.insert(1.0, message['parameters'])
        else:
            messagebox.showerror('请求失败','请求失败，服务器未返回下一页！')
        return

    def previous_chapter(self):
        """上一章"""
        if self.chapter == 0:
            messagebox.showwarning('警告！','已经是第一章！')
            return
        self.chapter = self.chapter - 1
        self.sc.send_message(MessageType.require_chapter, self.bkname + '*' + str(self.chapter))
        
        # 接收该章所处页数
        message = self.sc.recv_message()
        if message['type'] == MessageType.page_num:
            self.page_num = message['parameters']
            self.pagebtn['text'] = str(self.page_num+1) + '/' + str(self.total_page+1) # 更新页码
            print('《{}》第{}章位于第{}页'.format(self.bkname, self.chapter, message['parameters']))
        else:
            print('未能成功接收到该章页数！错误：{}'.format(message['type']))
            return

        # 接收该页
        message = self.sc.recv_message()
        if not message:
            messagebox.showerror('连接失败', 'QAQ 网络出现了问题，请稍后再试~')
        elif message['type'] == MessageType.no_book:
            messagebox.showerror('请求失败', '查无此书，请返回刷新书籍列表！')
        elif message['type'] == MessageType.send_page:
            print('成功接收第{}章'.format(self.chapter))
            self.text.delete('1.0', 'end') # 清空text文本框
            if message['parameters'][0] == '#':
                message['parameters'] = message['parameters'][1:]
            self.text.insert(1.0, message['parameters'])
        else:
            messagebox.showerror('请求失败','请求失败，服务器未返回上一章！')
        return

    def next_chapter(self):
        """下一章"""
        if self.chapter == self.total_chapter:
            messagebox.showwarning('警告！','已经是最后一章！')
            return     
        self.chapter = self.chapter + 1
        self.sc.send_message(MessageType.require_chapter, self.bkname + '*' + str(self.chapter))
        
        # 接收该章所处页数
        message = self.sc.recv_message()
        if message['type'] == MessageType.page_num:
            self.page_num = message['parameters']
            self.pagebtn['text'] = str(self.page_num+1) + '/' + str(self.total_page+1) # 更新页码
            print('《{}》第{}章位于第{}页'.format(self.bkname, self.chapter, message['parameters']))
        else:
            print('未能成功接收到该章页数！错误：{}'.format(message['type']))
            return

        # 接收该页
        message = self.sc.recv_message()
        if not message:
            messagebox.showerror('连接失败', 'QAQ 网络出现了问题，请稍后再试~')
        elif message['type'] == MessageType.no_book:
            messagebox.showerror('请求失败', '查无此书，请返回刷新书籍列表！')
        elif message['type'] == MessageType.send_page:
            print('成功接收第{}章'.format(self.chapter))
            self.text.delete('1.0', 'end') # 清空text文本框
            if message['parameters'][0] == '#':
                message['parameters'] = message['parameters'][1:]
            self.text.insert(1.0, message['parameters'])
        else:
            messagebox.showerror('请求失败','请求失败，服务器未返回下一章！')
        return
        
    def update_bookmark(self):
        """关闭时调用，更新书签"""
        # 发送 用户名 + 书名 + 页数
        self.sc.send_message(MessageType.update_bookmark, self.user + '*' + self.bkname + '*' + str(self.page_num))
        self.master.destroy()
        return