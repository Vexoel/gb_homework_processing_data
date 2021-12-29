from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from instagramparser.spiders.instagram import InstagramSpider
from instagramparser import settings

if __name__ == '__main__':
    users = set()

    while True:
        user = input("Введите nickname (пустой ввод завершение): ").strip()
        if user:
            users.add(user)
        else:
            break

    process_settings = Settings()
    process_settings.setmodule(settings)

    process = CrawlerProcess(settings=process_settings)

    process.crawl(InstagramSpider, users=users)

    process.start()
