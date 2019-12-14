# Network-Pj-BookReader
Network Course Final Project  

## 题目说明
**简单的小说阅读器的设计**

- 服务器端保存小说文本（txt格式的即可）
- 客户可以打开对应的文本，翻页，翻章，跳页，书签，下载，关闭等
- 建议最好有图形界面，因为是txt格式，所谓的“页”可以通过规定每次内容包含的字节来规定

## 环境
- python 3.7

## 实现思路
实现书签功能意味着肯定是要登陆的，而且每个用户需要维护一个书签表。整个书不能是简单的书，应该有划分的形式。这个对书的划分应该在服务器端完成，阅读时客户端不维护整本书，所看的每一页都需要让服务器发送来。体现小客户端大服务器的思想。章通过txt文本里面的空行来实现，默认规定只有章和章之间可以存在空行，遇到空行就分章。页通过规定传送的字节来规定，当遇到章末尾时默认中断该页。能算则算，尽量不储存。用户书签可以统一放到用户信息文件夹下面，当用户打开一本书时，查找该用户信息里有没有这本书，如果有则加载书签，默认打开上次阅读的位置。

所以服务器需要维护：用户名单，包含信息有用户名，密码，阅读过小说的书签（打开一本就加一个，打开书的时候遍历这个列表）。服务器不维护书籍表，在传的时候直接遍历books把文件名传过去。如果要实现评论的话直接弄一个review.txt，要是有书有评论就给他在里面整个评论表。

实现时最理想的状态是建立`secure channel`后，不管啥子操作，客户端发的还是服务器发的，都完全经过这个通道。这个通道应当是一个完整的封装，不和应该和下面的封装混杂。

## 代码结构
1. protocol 协议
    - `data_conversion` 原始数据与byte转换
        - `from_byte.py` byte格式数据解码为本来的数据
        - `to_byte.py` 各种类型数据编码为byte格式
    - `secure_transmission` 加密传输
        - `cryptogram.py` 生成密码
        - `secure_channel.py` 使用生成的密码建立安全通道用于数据传输
    - `utils` 
        - `__init__` longtobyte转化int为byte；
        - `read_config.py` 阅读config.json
    - `message_type` 不同种类和含义的信息对应的数字

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

## 封装说明
因为需要传输电子书（txt文件）和状态，用户名，评论等非文件数据，所以我们提供两种传输方式——文件传输（file）和数据传输（data），针对这两种数据分别进行封装。在数据封装之上再提供一层加密封装。

我们对每个数据都做了封装
- 个体数据的封装结构为：
`|-- Type of params (1 Byte) --|-- Length of body (4 Bytes) --|-- Body--|`
- 一条信息的封装结构为：
`|-- Length of Message Body (4 Bytes) --|-- Length of AES padding (1 Byte) --|-- AES IV (16 Bytes) --|-- Message Body (CSON) --|`

在server的`__init__.py`文件中，首先获得4 Bytes的信息长度，再对其进行接收。

## 注释
### encode与pack
如果希望使用socket传输数据，那么需要将各种数据类型转化为byte类型（txt文件传输似乎不需要，因为本身就是`encode('utf-8')`了的string）。为了实现这一转化我们调用了各种各样的函数：
>- str: `encode('utf-8')`; `decode('utf-8')`
>- int: longtobyte
>- bool
>- float
>- dict
>- list

而如果我们想一口气传输多个（多种）类型的数据，那么就需要对这些数据进行打包，调用struct中的pack函数，所以实际上pack不起到转化为byte的作用，它只扮演了将多个数据打包的角色。

### 加密算法
crypto库 AES的CBC加密

![CBC加密](./Picture/CBC_encryption.svg.png)

![CBC解密](./Picture/CBC_decryption.svg.png)
