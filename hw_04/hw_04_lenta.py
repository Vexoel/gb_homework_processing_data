from typing import Container
from lxml import html
import requests
from urllib.parse import urljoin, urlparse
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from pprint import pprint

def add_news(p_collection, p_vacancy):
    try:
        p_collection.insert_one(p_vacancy)
    except DuplicateKeyError as e:
        pass

url = 'https://lenta.ru/'

header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}

response = requests.get(url, headers=header)

dom = html.fromstring(response.text)

links = []

list = dom.xpath('//div[contains(@class, "b-yellow-box__header")]/following-sibling::div[contains(@class, "item")]')

news_list = []

for i in list:
    link = i.xpath('./a/@href')[0]
    pprint(link)
    if link.find('extlink') == -1:
        links.append(i.xpath('./a/@href')[0])
    else:
        item = {}

        item['link'] = url + link[1:]
        item['_id'] = link.replace('/', '')
        item['title'] = i.xpath('./a/text()')[0]
        item['source'] = 'lenta.ru'
        dict = link.split('/')
        item['time'] = dict[4] + '.' + dict[3] + '.' + dict[2]

        news_list.append(item)

for link in links:
    item = {}

    response = requests.get(url + link[1:], headers=header)
    
    dom = html.fromstring(response.text)

    container = dom.xpath('//div[contains(@class, "b-topic__header")]')[0]

    item['link'] = url + link[1:]
    item['_id'] = link.replace('/', '')
    item['title'] = container.xpath('.//h1[contains(@class, "b-topic__title")]/text()')[0]
    item['source'] = 'lenta.ru'
    item['time'] = datetime.fromisoformat(container.xpath('.//time/@datetime')[0]).strftime('%d.%m.%Y %H:%M')

    news_list.append(item)

client = MongoClient('127.0.0.1', 27017)

db = client['news']

lenta_news = db.lenta_news

for item_news in news_list:
    add_news(lenta_news, item_news)

for n in lenta_news.find():
    pprint(n)
