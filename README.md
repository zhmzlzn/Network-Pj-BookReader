# Network-Pj-BookReader
Network Course Final Project  

## 题目说明
**简单的小说阅读器的设计**

- 服务器端保存小说文本（txt格式的即可）
- 客户可以打开对应的文本，翻页，翻章，跳页，书签，下载，关闭等
- 建议最好有图形界面，因为是txt格式，所谓的“页”可以通过规定每次内容包含的字节来规定

## 环境
- python 3.7
- tkinter
- Crypto

## 运行
开两个终端，一个执行`python run_server.py`运行服务器，一个执行`python run_client.py`运行客户端。一个服务器可以同时支持多个客户端。

## 功能 & 特色
- 用户注册
- 用户登陆
- 小说阅读
    - 书签：每次打开小说均会跳回上次关闭时的位置
    - 翻页、跳页
    - 翻章、跳章
- 小说下载
- 安全传输：采用AES的CBC加密，服务器与客户端刚启动时建立安全通道，之后所有信息都通过安全通道发送（被加密）
- 服务器多线程：可同时应对多个客户端

## 实现思路
实现书签功能意味着肯定是要登陆的，而且每个用户需要维护一个书签表。整个书不能是简单的书，应该有划分的形式。这个对书的划分应该在服务器端完成，阅读时客户端不维护整本书，所看的每一页都需要让服务器发送来。体现小客户端大服务器的思想。页通过规定传送的字节来规定，能算则算，尽量不储存。用户书签可以统一放到用户信息文件夹下面，当用户打开一本书时，查找该用户信息里有没有这本书，如果有则加载书签，默认打开上次阅读的位置。

所以服务器需要维护：用户名单，包含信息有用户名，密码，阅读过小说的书签（打开一本就加一个，打开书的时候遍历这个列表）。服务器不维护书籍表，在传的时候直接遍历books把文件名传过去。如果要实现评论的话直接弄一个review.txt，要是有书有评论就给他在里面整个评论表。

章通过在客户端维护一个列表来实现。在开始阅读的时候服务器按规则遍历全书，然后得到一个二维列表，每个子列表的元素是章名及开始的页数。之后我们跳章，翻章的操作便可以通过页来完成，直接在客户端找到指定应该去的页，然后用跳页实现。

## 对书的格式要求
- 书的最开头单独一行标明是中文书还是英文书，中文书用“C”，英文书用“E”
- 以UTF-8的格式保存
- 文件开头为书名和作者，前面不需要“#”
- 每章应该有标题，单独成行，标题前标注“#”，后无空格接标题

## 代码结构
1. protocol 协议
    - `data_conversion` 原始数据与byte转换
        - `from_byte.py` byte格式数据解码为本来的数据
        - `to_byte.py` 各种类型数据编码为byte格式
    - `secure_transmission` 加密传输
        - `cryptogram.py` 生成密码
        - `secure_channel.py` 使用生成的密码建立安全通道用于各类数据传输
    - `utils` 一些工具
        - `__init__` longtobyte转化int为byte；md5
        - `read_config.py` 阅读config.json
    - `message_type` 不同种类和含义的信息对应的数字

2. client 客户端
    - `forms` 界面
        - `bookshelf_form.py` 书架界面（书籍列表）
        - `login_form.py` 用户登陆界面
        - `reader_form.py` 阅读界面
        - `register_form.py` 用户注册界面
    - `memory` 通用储存，专门记录该客户端的通用信息
    - `__init__.py` 初始化客户端

3. server 服务器
    - `books` 服务器储存的书籍
    - `event` 存放应对各种请求的处理函数，一个处理函数放在一个文件中
        - `__init__.py` 为客户端不同的请求选择对应的处理函数
        - `login.py` 处理客户端登陆
        - `register.py` 处理客户端注册
        - `send_book.py` 发送整本书
        - `send_list.py` 发送书籍列表
        - `send_page.py` 发送指定书的指定页
        - `start_read.py` 客户端开始阅读，若有书签则发送书签页，否则发送第一页
        - `update_bookmark.py` 客户端关闭阅读界面时会发送当前阅读的页数，用此更新书签
        - `utils.py` 定义发送一页的大小和发送第n页的函数，供`event`文件夹中的其他文件调用
    - `__init__.py` 初始化服务器
    - `memory` 通用储存，记录服务器的通用信息
    - `users.txt` 已注册用户信息及书签
    
4. 其他
    - `config.json` 设置网址、端口和密钥
    - `run_client.py` 启动客户端
    - `run_server.py` 启动服务器


## 协议说明
整个协议全部定义在`protocol`文件夹中，协议的核心代码位于`secure_channel.py`文件。我们发送的信息有两种类型——消息（message）和文件（file）

1. 消息（message）

原始数据 👉 转化为bytes（第一层封装） 👉 数据加密（第二层封装） 👉 最终发送的数据
- 第一层封装的结构为：
`A = |-- Type of Data (1 Byte) --|-- Length of Data (4 Bytes) --|-- Data --|`
- 第二层封装的结构为：
`B = |-- Length of Message Body (4 Bytes) --|-- Length of AES Padding (1 Byte) --|-- AES IV (16 Bytes) --|-- A --|`

2. 文件（file）

原始数据 👉 数据加密（由于规定了每次传输的大小，所以加密封装时不再封装总大小） 👉 最终发送的数据
- 封装结构为：
`|-- Length of AES Padding (1 Byte) --|-- AES IV (16 Bytes) --|-- One File's Part --|`

## 注释
### 1. `secure_channel`详解
#### 加密解密模块

`encrypt_data` 数据加密及加密信息封装（不包含计算信息总长度）

`decrypt_data` 数据解密
#### 发送消息

`send_message` 发送消息，完成数据类型转化封装和发送封装

`recv_message` 接收消息

#### 发送文件
`send_file` 发送一个txt文件，先发送文件总大小，后循环发送，也无需数据类型转化

`recv_file` 循环接收一个文件

### 2. encode与pack
如果希望使用socket传输数据，那么需要将各种数据类型转化为byte类型（txt文件传输似乎不需要，因为本身就是`encode('utf-8')`了的string）。为了实现这一转化我们调用了各种各样的函数：
>- str: `encode('utf-8')`; `decode('utf-8')`
>- int: longtobyte
>- bool
>- float
>- dict
>- list

而如果我们想一口气传输多个（多种）类型的数据，那么就需要对这些数据进行打包，调用struct中的pack函数，所以实际上pack不起到转化为byte的作用，它只扮演了将多个数据打包的角色。

### 3. 页和章
- 计算页时，新的一章会另起一页。
- 初始化时服务器直接发送全书的章节列表，保存在客户端。之后所有对于章的操作（翻章、跳章）都由客户端统一转化为对于页的操作。服务器只处理要求某一页而不处理要求某一章。

### 4. 加密算法
crypto库 AES的CBC加密

![CBC加密](./Picture/CBC_encryption.svg.png)

![CBC解密](./Picture/CBC_decryption.svg.png)

## 感谢
我的加密协议和多线程框架学习自`@KevinWang15`学长的[代码](https://github.com/KevinWang15/network-pj-chatroom)，稍有改动，在此表达感谢！
