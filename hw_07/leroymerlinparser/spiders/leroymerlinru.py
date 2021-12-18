import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader
from leroymerlinparser.items import LeroymerlinparserItem


class LeroymerlinruSpider(scrapy.Spider):
    name = 'leroymerlinru'
    allowed_domains = ['leroymerlin.ru']
    start_urls = ['https://leroymerlin.ru/catalogue/gvozdi/']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath('//a[@data-qa-pagination-item="right"]/@href').get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath('//a[@data-qa="product-name"]/@href').getall()

        for link in links:
            yield response.follow(link, callback=self.parse_item)


    def parse_item(self, response: HtmlResponse):
        loader = ItemLoader(item=LeroymerlinparserItem(), response=response)

        loader.add_value('url', response.url)

        loader.add_xpath('_id', '//span[@slot="article"]/@content')
        loader.add_xpath('name', '//h1[@slot="title"]/text()')
        loader.add_xpath('price', '//uc-pdp-price-view[@class="primary-price"]')
        loader.add_xpath('photos', '//picture[@slot="pictures"]/source[1]/@srcset')
        loader.add_xpath('specifications', '//div[@class="def-list__group"]')

        yield loader.load_item()
