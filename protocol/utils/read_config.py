'''解析config.json文件'''
import json # 解析JSON对象的库
from pprint import pprint # 提供了打印出任何python数据结构类和方法

with open('config.json') as config_file:
    config = json.load(config_file) # 将JSON对象转化为了python对象


def get_config():
    return config # 返回解码后生成的python对象
