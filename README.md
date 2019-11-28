# Network-Pj-BookReader
Network Course Final Project  

## 题目说明
**简单的小说阅读器的设计**

- 服务器端保存小说文本（txt格式的即可）
- 客户可以打开对应的文本，翻页，翻章，跳页，书签，下载，关闭等
- 建议最好有图形界面，因为是txt格式，所谓的“页”可以通过规定每次内容包含的字节来规定

## 环境
- python 3.7


## 结构
1. protocol 协议
    - 这里面是我们写的类http协议，是对数据的进一步封装和加密。

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


## 加密算法
crypto库 AES的CBC加密
![CBC加密](https://upload-images.jianshu.io/upload_images/4489364-56f2d5b6aa5201b7.png)

![CBC解密](https://upload-images.jianshu.io/upload_images/4489364-3568e52e89616ec5.png)
