# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BookparserItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()     # id
    link = scrapy.Field()    # ссылка на книгу
    name = scrapy.Field()    # наименование книги
    authors = scrapy.Field()  # автор(ы)
    price = scrapy.Field()   # цена
    rating = scrapy.Field()  # рейтинг
