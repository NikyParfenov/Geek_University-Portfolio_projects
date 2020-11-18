"""
Parser of auto in Youla.ru using the next structure:
1. Advertisement title
2. List of photos url
3. List of technical data
4. Description
5. Author of an advertisement (url)
6. Phone number of an author
"""
import scrapy
from ..loaders import YoulaAutoLoader


class YoulaSpider(scrapy.Spider):
    name = 'youla'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']

    xpath = {
        'brands': '//div[@class="TransportMainFilters_brandsList__2tIkv"]//a[@class="blackLink"]/@href',
        'ads': '//div[@id="serp"]//article//a[@data-target="serp-snippet-title"]/@href',
        'pagination': '//div[contains(@class, "Paginator_block")]/a/@href',
    }

    # parsing start urls
    def parse(self, response, **kwargs):
        for url in response.xpath(self.xpath['brands']):
            yield response.follow(url, callback=self.brand_parse)

    # parsing brands of auto
    def brand_parse(self, response, **kwargs):
        for url in response.xpath(self.xpath['pagination']):
            yield response.follow(url, callback=self.brand_parse)

        for url in response.xpath(self.xpath['ads']):
            yield response.follow(url, callback=self.ads_parse)

    # parsing advertisements
    def ads_parse(self, response, **kwargs):
        loader = YoulaAutoLoader(response=response)
        loader.add_xpath('title', '//div[contains(@class, "AdvertCard_advertTitle")]/text()')
        loader.add_xpath('img', '//div[contains(@class, "PhotoGallery_block")]//img/@src')
        loader.add_xpath('owner', '//script[contains(text(), "window.transitState =")]/text()')
        loader.add_xpath('phone_num', '//script[contains(text(), "window.transitState =")]/text()')
        loader.add_value('url', response.url)
        loader.add_xpath('tech_data', '//div[contains(@class, "AdvertCard_specs")]'
                                      '//div[contains(@class, "AdvertSpecs")]')
        loader.add_xpath('description', '//div[contains(@class, "AdvertCard_descriptionInner")]/text()')
        yield loader.load_item()
