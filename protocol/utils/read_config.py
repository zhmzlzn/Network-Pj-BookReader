'''解析config.json文件'''
import json # 解析JSON对象的库

with open('config.json') as config_file:
    config = json.load(config_file) # 将JSON对象转化为了python对象


def get_config():
    return config # 返回解码后生成的python对象
