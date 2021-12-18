# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from itemloaders.processors import TakeFirst, MapCompose
import scrapy
import re


def to_int(value):
    try:
        return int(value)
    except:
        return value


def to_float(value):
    try:
        return float(value)
    except:
        return value


def parse_price_item(text, item, exp):
    matched = re.search(f'itemprop="{item}" content="{exp}"', text).group(0)

    return matched.split('=')[-1][1:-1]


def parse_price(value):
    price = parse_price_item(value, 'price', '\d+.\d+')
    currency = parse_price_item(value, 'priceCurrency', '\w+')

    return {'price': price,
            'currency': currency}


def parse_specifications(value):
    matched = re.search(f'dt class="def-list__term">[\d\D]+</dt', value).group(0)
    key = matched[26:-4]

    matched = re.search(f'dd class="def-list__definition">[\d\D]+</dd', value).group(0)
    value = matched[32:-4].strip()

    return {key: value}


class LeroymerlinparserItem(scrapy.Item):
    url = scrapy.Field(output_processor=TakeFirst())
    _id = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(to_int))
    name = scrapy.Field(output_processor=TakeFirst())

    # price_value = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(to_float))
    # price_currency = scrapy.Field(output_processor=TakeFirst())
    # price_unit = scrapy.Field(output_processor=TakeFirst())

    # price = scrapy.Field()

    photos = scrapy.Field()

    price = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(parse_price))

    specifications = scrapy.Field(input_processor=MapCompose(parse_specifications))
