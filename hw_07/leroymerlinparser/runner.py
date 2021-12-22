from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from leroymerlinparser.spiders.leroymerlinru import LeroymerlinruSpider
from leroymerlinparser import settings

if __name__ == '__main__':
    process_settings = Settings()
    process_settings.setmodule(settings)

    process = CrawlerProcess(settings=process_settings)

    process.crawl(LeroymerlinruSpider)

    process.start()

