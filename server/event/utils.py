import math
from protocol.message_type import MessageType
ONE_PAGE_WORDS = 1000

def send_page(sc, book_path, page_num):
    """发送书的一页"""
    with open(book_path, 'r', encoding='utf-8') as f:
        num = 0
        j = 0
        line = f.readline()
        while num <= page_num:
            s = ''
            if line:
                s += line
                line = f.readline()
                while line:
                    if line[0] == '#':
                        break
                    s += line
                    line = f.readline()
            if num + math.ceil(len(s) / ONE_PAGE_WORDS) - 1 < page_num: # 读的页数不够
                num += math.ceil(len(s) / ONE_PAGE_WORDS)
                continue
            elif num + math.ceil(len(s) / ONE_PAGE_WORDS) - 1 == page_num: # 读的页数正好
                j = ONE_PAGE_WORDS * (math.ceil(len(s) / ONE_PAGE_WORDS) - 1)
                num = num + math.ceil(len(s) / ONE_PAGE_WORDS)
            else: # 读的页数超了
                j = ONE_PAGE_WORDS * (page_num - num)
                num = page_num
                break
        sc.send_message(MessageType.send_page, s[j: j+ONE_PAGE_WORDS])
        print('已发送第{}页'.format(page_num))
    return