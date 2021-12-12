# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError


def str_to_float(str):
    try:
        num = float(str)
    except (ValueError, TypeError):
        num = None

    return num


def add_book(collection, item):
    try:
        collection.insert_one(item)
    except DuplicateKeyError as e:
        pass


class BookparserPipeline:
    def __init__(self):
        client = MongoClient('127.0.0.1', 27017)
        self.mongobase = client.books

    def process_item(self, item, spider):
        item['price']['new'] = str_to_float(item['price']['new'])

        if spider.name == 'book24ru':
            if item['price']['old']:
                item['price']['old'] = str_to_float(item['price']['old'][:-3])
            item['rating'] = str_to_float(item['rating'].replace(',', '.'))
        else:
            item['price']['old'] = str_to_float(item['price']['old'])
            item['rating'] = str_to_float(item['rating'])



        add_book(self.mongobase[spider.name], item)

        return item
