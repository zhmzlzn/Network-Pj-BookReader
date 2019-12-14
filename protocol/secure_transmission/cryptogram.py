"""
生成密钥
"""
from random import randint
from protocol.utils.read_config import get_config
from protocol.utils import long_to_bytes
import hashlib

def is_prime(num, test_count):
    """判断是否为质数（试test_count以内的数来判断）"""
    if num == 1:
        return False
    if test_count >= num:
        test_count = num - 1
    for x in range(test_count):
        val = randint(1, num - 1)
        if pow(val, num-1, num) != 1:
            return False
    return True

def generate_big_prime(n):
    """得到一个由n生成的质数"""
    found_prime = False
    while not found_prime:
        p = randint(2**(n-1), 2**n)
        if is_prime(p, 1000):
            return p

config = get_config()

base = config['crypto']['base']
modulus = config['crypto']['modulus']
secret = generate_big_prime(12) # 得到一个质数

my_secret = base ** secret % modulus # 由base、modulus和一个质数共同生成己方密钥

def get_shared_secret(their_secret):
    """使用对方密钥生成共同密钥"""
    return hashlib.sha256(long_to_bytes(their_secret ** secret % modulus)).digest()