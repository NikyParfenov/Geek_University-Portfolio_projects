# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline


class GbparsersPipeline:
    def __init__(self):
        db_client = MongoClient('mongodb://localhost:27017')
        self.db = db_client['db_parse_10-2020']

    def process_item(self, item, spider):
        # collection = self.db[spider.name]
        collection = self.db[type(item).__name__]
        collection.insert_one(item)
        return item


class GbparsersImagePipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        if item.get('img'):
            for url in item.get('img'):
                try:
                    yield Request(url)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        if item.get('img'):
            item['img'] = [itm[1] for itm in results if itm[0]]
        return item
