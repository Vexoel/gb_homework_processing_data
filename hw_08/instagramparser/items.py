# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


# ProfileItem
class InstagramProfileItem(scrapy.Item):
    user_id = scrapy.Field()
    user_name = scrapy.Field()
    user_img = scrapy.Field()


# User2FollowerItem
class InstagramUser2FollowerItem(scrapy.Item):
    user_id = scrapy.Field()
    follower_id = scrapy.Field()