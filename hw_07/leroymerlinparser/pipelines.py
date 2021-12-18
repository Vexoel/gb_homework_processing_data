# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import hashlib
import os

import scrapy
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient
from datetime import datetime


class LeroymerlinparserPipeline:
    def process_item(self, item, spider):
        tmp = {}

        for spec in item['specifications']:
            tmp.update(spec)

        item['specifications'] = tmp

        return item


class LeroymerlinparserImgPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img_link in item['photos']:
                try:
                    yield scrapy.Request(img_link)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        item['photos'] = [itm[1]['path'] for itm in results if itm[0]]

        return item

    # def file_path(self, request, response=None, info=None, item=None):
    #     return f"{item['_id']}/{request.url.split('/')[-1]}"


def add_item(collection, item):
    if collection.find({'_id': {"$in": item['_id']}}):
        collection.delete_one({'_id': item['_id']})

    collection.insert_one(item)


class LeroymerlinparserDatabasePipeline:
    def __init__(self):
        client = MongoClient('127.0.0.1', 27017)
        self.mongobase = client.leroymerlin

    def process_item(self, item, spider):
        mongodb_item = {'_id': item['_id'],
                        'url': item['url'],
                        'name': item['name'],
                        'price': item['price'],
                        'photos': item['photos']}

        add_item(self.mongobase[datetime.today().strftime('%Y-%m-%d')], mongodb_item)

        return item