import threading
import socket
import time
import operator
import os
import struct

def download(connect):
    """
    客户端下载
    """
    #获取文件目录
    files = os.listdir()
    #用于传输文件目录的字符串
    liststr = ''
    #将所有文件名传入字符串中
    for i in files:
        liststr += i + '\n'
    #如果文件列表为空，将不继续执行下载任务
    if operator.eq(liststr,''): 
        connect.send(''.encode())
    #如果文件列表不为空，开始下载任务
    else :
        #向客户端传送文件列表
        connect.send(liststr.encode())
        while  True:
            #获取客户端要下载的文件名，如果不存在就继续输入
            filename = connect.recv(100).decode()
            if filename not in files:
                connect.send('no'.encode())
            else:
                connect.send('yes'.encode())
                break
        #将文件信息打包发送给客服端
        fhead = struct.pack('128sI',filename.encode(),os.stat(filename).st_size)
        connect.send(fhead)
        #传送文件信息
        with open(filename,'rb') as f:
            while True:
                filedata = f.read(1024)
                if not filedata:
                    break
                connect.send(filedata)
        #存储到日志中
        print ('%s\n下载文件:\n%s\n成功\n\n'%(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),filename))
        os.chdir('..')
        with open('data.log','a') as f:
            f.write('%s\n下载文件:\n%s\n成功\n\n'%(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),filename))
        os.chdir('files')

        