import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem


class LabirintruSpider(scrapy.Spider):
    name = 'labirintru'
    allowed_domains = ['labirint.ru']

    def __init__(self, search, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [f'https://www.labirint.ru/search/{search}/']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath('//a[@class="pagination-next__text" and @title="Следующая"]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        links = response.xpath('//a[@class="product-title-link"]/@href').getall()
        for link in links:
            yield response.follow(link, callback=self.book_parse)

    def book_parse(self, response: HtmlResponse):
        _id = response.url.split('/')[-2]
        link = response.url
        name = response.xpath('//div[@id="product-title"]/h1/text()').get()
        authors = response.xpath('//div[@class="authors"]/a[@data-event-label="author"]/text()').getall()
        price = {'old': response.xpath('//span[@class="buying-priceold-val-number"]/text()').get(),
                 'new': response.xpath('//span[@class="buying-pricenew-val-number"]/text()').get() if response.xpath(
                     '//span[@class="buying-pricenew-val-number"]/text()').get() else response.xpath(
                     '//span[@class="buying-price-val-number"]/text()').get(),
                 'currency': response.xpath('//span[@class="buying-pricenew-val-currency"]/text()').get()}
        rating = response.xpath('//div[@id="rate"]/text()').get()

        item = BookparserItem(_id=_id, link=link, name=name, authors=authors, price=price, rating=rating)

        yield item
