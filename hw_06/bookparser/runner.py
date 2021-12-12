from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from bookparser import settings
from bookparser.spiders.labirintru import LabirintruSpider
from bookparser.spiders.book24ru import Book24ruSpider

if __name__ == '__main__':
    search = input('Введите автора для поиска: ')

    process_settings = Settings()
    process_settings.setmodule(settings)

    process = CrawlerProcess(settings=process_settings)

    process.crawl(LabirintruSpider, search=search)
    process.crawl(Book24ruSpider, search=search)

    process.start()
