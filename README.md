# Network-Pj-BookReader
Network Course Final Project  

@[TOC]目录

## 0 题目说明
**简单的小说阅读器的设计**

- 服务器端保存小说文本（txt格式的即可）
- 客户可以打开对应的文本，翻页，翻章，跳页，书签，下载，关闭等
- 建议最好有图形界面，因为是txt格式，所谓的“页”可以通过规定每次内容包含的字节来规定

## 1 环境
- python 3.7

## 2 代码结构
1. protocol 协议
    - `secure` AES加密层
        - `cryptogram.py` 生成密码
        - `secure_channel.py` 使用生成的密码建立安全通道用于数据传输
    - `utils` 
        - `__init__` longtobyte转化int为byte；
        - `read_config.py` 阅读config.json

2. client 客户端
    - `forms` 界面
    - `component` 组件
    - `memory` 通用储存，专门记录该客户端的通用信息
    - `__init__.py` 启动客户端

3. server 服务器
    - `event_handler` 对各种请求的处理
    - `memory` 通用储存，记录服务器的通用信息
    - `__init__.py` 启动服务器
    - `books` 服务器储存的书籍

## 3 封装说明

## 4 注释
### 4.1 encode与pack
如果希望使用socket传输数据，那么需要将各种数据类型转化为byte类型（txt文件传输似乎不需要，因为本身就是`encode('utf-8')`了的string）。为了实现这一转化我们调用了各种各样的函数：
>- str: `encode('utf-8')`; `decode('utf-8')`
>- int: longtobyte
>- bool
>- float
>- dict
>- list
而如果我们想一口气传输多个（多种）类型的数据，那么就需要对这些数据进行打包，调用struct中的pack函数，所以实际上pack不起到转化为byte的作用，它只扮演了将多个数据打包的角色。

### 4.2 加密算法
crypto库 AES的CBC加密
![CBC加密](https://upload-images.jianshu.io/upload_images/4489364-56f2d5b6aa5201b7.png)

![CBC解密](https://upload-images.jianshu.io/upload_images/4489364-3568e52e89616ec5.png)
