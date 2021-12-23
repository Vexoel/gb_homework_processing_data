# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from pprint import pprint

import scrapy
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline

from instagramparser.items import InstagramProfileItem


class InstagramparserImgPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if isinstance(item, InstagramProfileItem):
            if item['user_img']:
                try:
                    yield scrapy.Request(item['user_img'])
                except Exception as e:
                    print(e)
        else:
            return item

    def item_completed(self, results, item, info):
        if isinstance(item, InstagramProfileItem):
            item['user_img'] = [itm[1]['path'] for itm in results if itm[0]]

        return item


def add_item(collection, item):
    if collection.find({'_id': {"$in": item['_id']}}):
        collection.delete_one({'_id': item['_id']})

    collection.insert_one(item)


class InstagramparserDatabasePipeline:
    def __init__(self):
        client = MongoClient('127.0.0.1', 27017)
        self.mongobase = client.instagram

    def process_item(self, item, spider):
        if isinstance(item, InstagramProfileItem):
            collection = 'profile'

            mongodb_item = {'_id': item['user_id'],
                            'user_name': item['user_name'],
                            'user_img': item['user_img']}
        else:
            collection = 'profile2follower'

            mongodb_item = {'_id': str(item['user_id']) + '|' + str(item['follower_id']),
                            'user_id': item['user_id'],
                            'follower_id': item['follower_id']}

        add_item(self.mongobase[collection], mongodb_item)

        yield item
