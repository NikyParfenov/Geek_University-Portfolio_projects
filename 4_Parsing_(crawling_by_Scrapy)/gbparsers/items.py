# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class YoulaAutoItem(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field()
    img = scrapy.Field()
    url = scrapy.Field()
    tech_data = scrapy.Field()
    description = scrapy.Field()
    owner = scrapy.Field()
    phone_num = scrapy.Field()


class HeadHunterJobsItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    salary = scrapy.Field()
    description = scrapy.Field()
    skills = scrapy.Field()
    owner_url = scrapy.Field()


class HeadHunterCompaniesItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    company_url = scrapy.Field()
    field_of_work = scrapy.Field()
    description = scrapy.Field()


class InstagramTagsItem(scrapy.Item):
    _id = scrapy.Field()
    date_parse = scrapy.Field()
    data = scrapy.Field()
    img = scrapy.Field()


class InstagramPostsItem(InstagramTagsItem):
    pass


class InstagramUserFollowItems(scrapy.Item):
    _id = scrapy.Field()
    user_id = scrapy.Field()
    user_name = scrapy.Field()
    follow_id = scrapy.Field()
    follow_name = scrapy.Field()
