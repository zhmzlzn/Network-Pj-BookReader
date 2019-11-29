from Myprotocol.header import Header
import struct
import socket
import os

def send_file(sock, fname):
    """
    发送给客户端名为name的文件
    
    sock：用于传输的socket
    name：要传输的文件名
    """
    filename = connect.recv(1024).decode('utf-8') # 解码得到数据
    #str = message.split('\n')
    files = os.listdir() # files为当前目录下的文件列表
    while True:
        if filename in files: # 如果这个文件在列表里
            break
    # 传输分为两个部分，先传输文件头，再传输文件的内容
    fhead = struct.pack('128sI',filename.encode(),os.stat(filename).st_size) # 文件名和文件大小
    connect.send(fhead)
    
    with open(filename,'rb') as f:
            while True:
                filedata = f.read(1024)
                if not filedata:
                    break
                connect.send(filedata)
