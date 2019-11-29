from Myprotocol.header import Header
import struct
import socket
import os

def require_file(sock, name):
    """
    要求从服务器获得名为name的文件
    
    sock：用于传输的socket
    name：要传输的文件名
    """
    sock.send(name.encode('utf-8'))
    FILEINFO_SIZE = struct.calcsize('128sI') # “文件名 + 文件大小”的总大小
    try:
        fhead = sock.recv(FILEINFO_SIZE)
        filename, fileseze = struct.unpack('128sI', fhead)
        with open('new_'+filename.decode().strip('\00'),'wb') as f: # 创建这个文件
        ressize = filesize # 剩下要接收的大小
            while True:
                if ressize>1024:
                    filedata = sock.recv(1024)
                else:
                    filedata = sock.recv(ressize)
                    f.write(filedata)
                    break
                if not filedata:
                    break
                f.write(filedata)
                ressize = ressize - len(filedata)
                if ressize <0:
                    break
        print ('文件传输成功!')
    except Exception as e:
        print (e)
        print ('文件传输失败!')
    return