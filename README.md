# python-BookReader
Network course final project  

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


## 加密算法
crypto库 md5算法