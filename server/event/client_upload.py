import threading
import socket
import time
import operator
import os
import struct

def run(socket):
    """
    客户端上传
    """
    FILEINFO_SIZE = struct.calcsize('128sI')
    try:
        #获取打包好的文件信息，并解包
        fhead = socket.recv(FILEINFO_SIZE)
        filename , filesize = struct.unpack('128sI',fhead)
        filename = filename.decode().strip('\00')
        #文件名必须去掉\00，否则会报错，此处为接收文件
        with open ('newnew_'+ filename,'wb') as f:
            ressize = filesize
            while True:
                if ressize>1024:
                    filedata = socket.recv(1024)
                else:
                    filedata = socket.recv(ressize)
                    f.write(filedata)
                    break
                if not filedata:
                    break
                f.write(filedata)
                ressize = ressize - len(filedata)
                if ressize <0:
                    break
        #存储到日志
        print ('%s\n传输文件:\n%s\n成功\n\n'%(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),filename))
        os.chdir('..')
        with open('data.log','a') as f:
            f.write('%s\n传输文件:\n%s\n成功\n\n'%(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),filename))
        os.chdir('files')
    except Exception as e:
        print ('%s\n传输文件:\n%s\n成功\n\n'%(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),filename))
        os.chdir('..')
        with open('data.log','a') as f:
            f.write('%s\n传输文件:\n%s\n失败\n\n'%(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),filename))
        os.chdir('files')