import scrapy
from scrapy.http import HtmlResponse
from bookparser.items import BookparserItem

class Book24ruSpider(scrapy.Spider):
    name = 'book24ru'
    allowed_domains = ['book24.ru']

    def __init__(self, search, **kwargs):
        super().__init__(**kwargs)
        self.page = 1
        self.search = search
        self.start_urls = [f'https://book24.ru/search/page-{self.page}/?q={self.search}/']

    def parse(self, response: HtmlResponse):
        links = response.xpath('//div[@class="catalog__product-list-holder"]//a[@class="product-card__name smartLink"]/@href').getall()
        for link in links:
            yield response.follow(link, callback=self.book_parse)

        self.page += 1
        yield response.follow(f'https://book24.ru/search/page-{self.page}/?q={self.search}/', callback=self.parse)

    def book_parse(self, response: HtmlResponse):
        _id = response.url.split('-')[-1][:-1]
        link = response.url
        name = response.xpath('//h1[@class="product-detail-page__title"]/text()').get()
        authors = response.xpath('//a[contains(@href,"author")]/@title').getall()
        price = {'old': response.xpath('//span[@class="app-price product-sidebar-price__price-old"]/text()').get(),
                 'new': response.xpath('//meta[@itemprop="price"]/@content').get(),
                 'currency': response.xpath('//meta[@itemprop="priceCurrency"]/@content').get()}
        rating = response.xpath('//span[@class="rating-widget__main-text"]/text()').get()

        item = BookparserItem(_id=_id, link=link, name=name, authors=authors, price=price, rating=rating)

        yield item