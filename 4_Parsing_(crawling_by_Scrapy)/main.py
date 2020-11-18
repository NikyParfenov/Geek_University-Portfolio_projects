import os
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gbparsers import settings
from dotenv import load_dotenv
from gbparsers.spiders.youla import YoulaSpider
from gbparsers.spiders.hh import HeadHunterSpider
from gbparsers.spiders.instagram import InstagramSpider

load_dotenv('.env')

if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule(settings)
    crawl_process = CrawlerProcess(settings=crawl_settings)
    crawl_process.crawl(YoulaSpider)
    crawl_process.crawl(HeadHunterSpider)
    crawl_process.crawl(InstagramSpider,
                        login=os.getenv('LOGIN'),
                        enc_password=os.getenv('ENC_PASSWORD'))
    crawl_process.start()
