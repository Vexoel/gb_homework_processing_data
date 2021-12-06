from lxml import html
import requests
import urllib.parse as urlparse
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from pprint import pprint

def get_news(container):
    item = {}
    item['link'] = container.xpath('.//a[@class="mg-card__link"]/@href')[0]
    item['link'].find('&persistent_id=')

    url_dict = dict(urlparse.parse_qsl(urlparse.urlparse(item['link']).query))

    try:
        item['_id'] = url_dict['persistent_id']
    except KeyError:
        pass

    item['title'] = container.xpath('.//h2[@class="mg-card__title"]/text()')[0]
    item['source'] = container.xpath('.//a[@class="mg-card__source-link"]/text()')[0]
    # item['time'] = datetime.strptime(
    #     datetime.today().strftime('%d/%m/%Y') + ' ' + contraiter.xpath('.//span[@class="mg-card-source__time"]/text()')[
    #         0],
    #     '%d/%m/%Y %H:%M')
    item['time'] = datetime.today().strftime('%d.%m.%Y') + ' ' + \
                   container.xpath('.//span[@class="mg-card-source__time"]/text()')[
                       0]
    return item


def add_news(p_collection, p_vacancy):
    try:
        p_collection.insert_one(p_vacancy)
    except DuplicateKeyError as e:
        pass


header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}

news_list = []

response = requests.get('https://yandex.ru/news/', headers=header)

if response.url.find('showcaptcha') == -1:
    dom = html.fromstring(response.text)

    news = dom.xpath('//a[contains(text(),"Интересное")]/../../following::div[1]')[0]

    main_news = news.xpath('./div[@class="mg-grid__col mg-grid__col_xs_4"]')[0]

    news_list.append(get_news(main_news))

    other_news = news.xpath('.//div[@class="mg-grid__col mg-grid__col_xs_6"]')

    for item_news in other_news:
        news_list.append(get_news(item_news))

    client = MongoClient('127.0.0.1', 27017)

    db = client['news']

    ya_news = db.ya_news

    for item_news in news_list:
        add_news(ya_news, item_news)

    for n in ya_news.find():
        pprint(n)
else:
    print('Captcha')