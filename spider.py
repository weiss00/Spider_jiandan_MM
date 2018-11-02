# -*- coding:utf-8 -*-


"__author__" == "weiss"

import time
import os
from hashlib import md5
import requests
from requests.exceptions import RequestException
import base64
from pyquery import PyQuery as pq
import pymongo
from config import *
from multiprocessing import Pool

# 因为煎蛋网妹子图加密，所以需要找到妹子图片的hash值并base64解码即可得到图片链接
# ENTER_NUMBER = int(input('Please enter a number: '))

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 5.2) AppleWebKit/534.30 (KHTML, like Gecko) Chrome/12.0.742.122 Safari/534.30'
}

client = pymongo.MongoClient(MONGO_URL, MONGO_PORT)
db = client[MONGO_DB]


def get_index(offset):
    pri_url = 'http://jandan.net/ooxx/page-' + str(offset)
    try:
        time.sleep(1.5)
        response = requests.get(pri_url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None


def parse_index(html):
    doc = pq(html)
    items = doc('.row .text .img-hash').items()
    for item in items:
        yield item.text()


def base64_decode(hash_content):
    #  此方法为爬妹子图的关键，因为妹子图有加密hash值需要base64解码，
    # 解码后获取到的链接是小图片，观察一下将连接中的'mw600'，替换成'large'则可怕渠道高清大图
    url = base64.b64decode(hash_content)
    url = (str(url, encoding='utf-8').replace('mw600', 'large'))
    yield url


def get_img(url):
    try:
        print('开始下载', url)
        time.sleep(0.5)
        response = requests.get('http:' + url)
        if response.status_code == 200:
            save_image(response.content)
        return None
    except RequestException:
        return None


def save_image(content):
    # MD5去重
    file_path = '{0}/{1}.{2}'.format(os.getcwd(), md5(content).hexdigest(), 'jpg')
    print(file_path)
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)
            f.close()


def main(offset):
    html = get_index(offset)
    if html:
        urls = parse_index(html)
        for i in urls:
            decode_url = base64_decode(i)
            for j in decode_url:
                get_img(j)


#  加入进程池提高爬取效率，顺便加了延时，毕竟都不容易
if __name__ == '__main__':
    # main()
    pool = Pool()
    groups = ([x for x in range(GROUP_START, GROUP_END + 1)])
    pool.map(main, groups)
    pool.close()
    pool.join()