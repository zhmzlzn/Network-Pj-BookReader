import socket
import threading
from threading import Thread
import sys
import time
import random
from queue import Queue

host = '127.0.0.1'
port = 8998
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port)) # 绑定host和port到socket
s.listen(3) # 在拒绝连接之前，操作系统可以挂起的最大连接数量

class ThreadPoolManger():
    """线程池管理器"""
    def __init__(self, thread_num):
        """定义线程数量"""
        self.work_queue = Queue() # 构造一个FIFO队列，maxsize可以限制队列的大小
        self.thread_num = thread_num
        self.__init_threading_pool(self.thread_num)

    def __init_threading_pool(self, thread_num):
        """初始化线程池，创建指定数量的线程池"""
        for i in range(thread_num):
            thread = ThreadManger(self.work_queue)
            thread.start()

    def add_job(self, func, *args):
        """将任务放入队列，等待线程池阻塞读取，参数是需要被执行的函数和函数的参数"""
        self.work_queue.put((func, args))


class ThreadManger(Thread):
    """定义线程类，继承threading.Thread，需要参数队列"""
    def __init__(self, work_queue):
        Thread.__init__(self)
        self.work_queue = work_queue
        self.daemon = True # deamon 守护？

    def run(self):
        """启动线程"""
        while True:
            # 得到一个queue中的内容，由于我们定义接收的是两个内容，一个要执行的函数，一个参数，所以这里也拆解成两个
            target, args = self.work_queue.get() 
            target(*args) # 要执行的函数执行给该函数的参数
            self.work_queue.task_done() # get得到的任务完成，提示可以停止阻塞，和get搭配出现

# 创建一个有4个线程的线程池
thread_pool = ThreadPoolManger(4)

# 处理http请求，这里简单返回200 hello world
def handle_request(conn_socket):
    recv_data = conn_socket.recv(1024) # 这里应该成用secure channel接收
    reply = b'HTTP/1.1 200 OK \r\n\r\n'
    reply += b'hello world'
    print ('thread %s is running ' % threading.current_thread().name)
    conn_socket.send(reply) # 这里改为secure channel发送
    conn_socket.close()

# 循环等待接收客户端请求
while True:
    conn_socket, addr = s.accept() # 阻塞等待请求
    # 一旦有请求了，把socket扔到我们指定处理函数handle_request处理，等待线程池分配线程处理
    thread_pool.add_job(handle_request, *(conn_socket, ))

s.close()

