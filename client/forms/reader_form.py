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
        self.chapter = [] # 当前书的章节列表
        self.chap_num = 0 # 当前所在的章数（由章节列表计算得出）
        self.total_chapter = 0 # 当前书的总章节数（由章节列表计算得出）
        self.createForm()
        master.protocol("WM_DELETE_WINDOW", self.update_bookmark)

    def createForm(self):
        self.master.title("Jack的阅读器")

        # 章节
        self.chapbtn = Button(self, command=self.jump_chapter)
        self.chapbtn.pack(side=TOP, fill=X, expand=YES)

        self.text = Text(self, height=35)
        self.text.pack(side=TOP, fill=BOTH)
        self.start_read()

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

    def get_chapter(self):
        """通过章节列表获得当前页所处的章序号"""
        for i in range(self.total_chapter):
            if self.page_num >= self.chapter[i][1]:
                if i == self.total_chapter - 1 or self.page_num < self.chapter[i+1][1]:
                    return i
    
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

        # 接收总页数
        message = self.sc.recv_message()
        if message['type'] == MessageType.total_page:
            self.total_page = message['parameters']
            print('《{}》共{}页'.format(self.bkname, message['parameters']))
        else:
            print('未能成功接收到总页数！错误：{}'.format(message['type']))
            return

        # 接收章节列表
        message = self.sc.recv_message()
        if message['type'] == MessageType.send_chapter:
            self.chapter = message['parameters']
            self.total_chapter = len(self.chapter)
            self.chap_num = self.get_chapter()
            self.chapbtn['text'] = self.chapter[self.chap_num][0] # 更新要显示的章节名
            print('《{}》共{}章'.format(self.bkname, self.total_chapter))
        else:
            print('未能成功接收到章节列表！错误：{}'.format(message['type']))
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
            self.chap_num = self.get_chapter()
            self.chapbtn['text'] = self.chapter[self.chap_num][0] # 更新要显示的章节名
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
            self.chap_num = self.get_chapter()
            self.chapbtn['text'] = self.chapter[self.chap_num][0] # 更新要显示的章节名
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
            self.chap_num = self.get_chapter()
            self.chapbtn['text'] = self.chapter[self.chap_num][0] # 更新要显示的章节名
            self.pagebtn['text'] = str(self.page_num+1) + '/' + str(self.total_page+1) # 更新页码
            self.text.delete('1.0', 'end') # 清空text文本框
            if message['parameters'][0] == '#':
                message['parameters'] = message['parameters'][1:]
            self.text.insert(1.0, message['parameters'])
        else:
            messagebox.showerror('请求失败','请求失败，服务器未返回下一页！')
        return

    def jump_chapter(self):
        """跳章"""
        chap_name = self.ask_chap()
        if chap_name is None: return
        for i in range(self.total_chapter):
            if chap_name == self.chapter[i][0]:
                self.chap_num = i
                self.page_num = self.chapter[self.chap_num][1]
                self.pagebtn['text'] = str(self.page_num+1) + '/' + str(self.total_page+1) # 更新页码
                self.chapbtn['text'] = self.chapter[self.chap_num][0] # 更新要显示的章节名        

                self.sc.send_message(MessageType.require_page, self.bkname + '*' + str(self.page_num))
                # 接收该页
                message = self.sc.recv_message()
                if not message:
                    messagebox.showerror('连接失败', 'QAQ 网络出现了问题，请稍后再试~')
                elif message['type'] == MessageType.no_book:
                    messagebox.showerror('请求失败', '查无此书，请返回刷新书籍列表！')
                elif message['type'] == MessageType.send_page:
                    print('成功接收第{}章'.format(self.chap_num))
                    self.text.delete('1.0', 'end') # 清空text文本框
                    if message['parameters'][0] == '#':
                        message['parameters'] = message['parameters'][1:]
                    self.text.insert(1.0, message['parameters'])
                else:
                    messagebox.showerror('请求失败','请求失败，服务器未返回下一章！')
                return

    def ask_chap(self):
        """章节列表弹窗"""
        dialog = ChapterList(self.chapter)
        self.wait_window(dialog)
        return dialog.chap_name
    
    def previous_chapter(self):
        """上一章"""
        if self.chap_num == 0:
            messagebox.showwarning('警告！','已经是第一章！')
            return
        self.chap_num = self.chap_num - 1
        self.page_num = self.chapter[self.chap_num][1]
        self.pagebtn['text'] = str(self.page_num+1) + '/' + str(self.total_page+1) # 更新页码
        self.chapbtn['text'] = self.chapter[self.chap_num][0] # 更新要显示的章节名

        self.sc.send_message(MessageType.require_page, self.bkname + '*' + str(self.page_num))
        # 接收该页
        message = self.sc.recv_message()
        if not message:
            messagebox.showerror('连接失败', 'QAQ 网络出现了问题，请稍后再试~')
        elif message['type'] == MessageType.no_book:
            messagebox.showerror('请求失败', '查无此书，请返回刷新书籍列表！')
        elif message['type'] == MessageType.send_page:
            print('成功接收第{}章'.format(self.chap_num))
            self.text.delete('1.0', 'end') # 清空text文本框
            if message['parameters'][0] == '#':
                message['parameters'] = message['parameters'][1:]
            self.text.insert(1.0, message['parameters'])
        else:
            messagebox.showerror('请求失败','请求失败，服务器未返回上一章！')
        return

    def next_chapter(self):
        """下一章"""
        if self.chap_num >= self.total_chapter-1:
            messagebox.showwarning('警告！','已经是最后一章！')
            return     
        self.chap_num = self.chap_num + 1
        self.page_num = self.chapter[self.chap_num][1]
        self.pagebtn['text'] = str(self.page_num+1) + '/' + str(self.total_page+1) # 更新页码
        self.chapbtn['text'] = self.chapter[self.chap_num][0] # 更新要显示的章节名        

        self.sc.send_message(MessageType.require_page, self.bkname + '*' + str(self.page_num))
        # 接收该页
        message = self.sc.recv_message()
        if not message:
            messagebox.showerror('连接失败', 'QAQ 网络出现了问题，请稍后再试~')
        elif message['type'] == MessageType.no_book:
            messagebox.showerror('请求失败', '查无此书，请返回刷新书籍列表！')
        elif message['type'] == MessageType.send_page:
            print('成功接收第{}章'.format(self.chap_num))
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

class ChapterList(tk.Toplevel):
    def __init__(self, chapter):
        super().__init__()
        self.chapter = chapter
        self.chap_name = ''
        self.createForm()        

    def createForm(self):
        self.title("请选择章节")

        self.sb = Scrollbar(self)
        self.sb.pack(side=RIGHT, fill=Y)

        self.chaplist = Listbox(self, height=15, width=40, yscrollcommand=self.sb.set)
        for chap in self.chapter:
            self.chaplist.insert(END, chap[0])
        self.chaplist.pack(side=TOP, fill=BOTH)
        
        self.sb.config(command=self.chaplist.yview)

        self.buttonframe = Frame(self)
        self.buttonframe.pack(side=BOTTOM, fill=BOTH, expand=YES)
        self.jmpbtn = Button(self.buttonframe, text="跳转", command=self.jump)
        self.jmpbtn.pack(side=LEFT, fill=X, expand=YES)
        self.cncbtn = Button(self.buttonframe, text="取消", command=self.cancel)
        self.cncbtn.pack(side=LEFT, fill=X, expand=YES)

    def jump(self):
        """回传选择的值"""
        self.chap_name = self.chaplist.get(self.chaplist.curselection()) # 得到选择的小说名
        self.destroy()

    def cancel(self):
        """取消，直接销毁窗口"""
        self.destroy()