"""
Instagram parser of the next data blocks:
1. Parse of hashtags with associated posts (parse date, data, photos url with saving its on a disk)
2. Parse of users followings and followers
"""
import scrapy
import json
from datetime import datetime
from ..items import InstagramTagsItem, InstagramPostsItem, InstagramUserFollowItems


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    __login_url = 'https://www.instagram.com/accounts/login/ajax/'
    pagination_url = '/graphql/query/'
    follow_types = {'followings': 'edge_follow',
                    'followers': 'edge_followed_by',
                    }
    query_hash = {'tags': '9b498c08113f1e09617a1703c22b2f32',
                  'followers': 'c76146de99bb02f6415203be841dd25a',
                  'followings': 'd04b0a864b4b54837c0d870b0e77e076',
                  }

    def __init__(self, login, enc_password, *args, **kwargs):
        # tags for parsing
        self.tags = ['python', 'pythonprogramming']
        # part of users url for parsing of followings and followers
        self.users = ['gal_gadot', 'katyperry']
        # self.users_follow = users
        self.__login = login
        self.__enc_password = enc_password
        super().__init__(*args, **kwargs)

    def parse(self, response, **kwargs):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                self.__login_url,
                method='POST',
                callback=self.parse,
                formdata={
                    'username': self.__login,
                    'enc_password': self.__enc_password,
                },
                headers={'X-CSRFToken': js_data['config']['csrf_token']},
            )
        except AttributeError as e:
            if response.json().get('authenticated'):
                for tag in self.tags:
                    yield response.follow(f'/explore/tags/{tag}/', callback=self.tag_parse, cb_kwargs={'param': tag})
                for user in self.users:
                    yield response.follow(f'/{user}/',
                                          callback=self.user_parse,
                                          )

    def tag_parse(self, response, **kwargs):
        # parse of input tags into Item structure
        hashtag = self.js_data_extract(response)['entry_data']['TagPage'][0]['graphql']['hashtag']
        yield InstagramTagsItem(date_parse=datetime.now(),
                                data={'id': hashtag['id'], 'name': hashtag['name']},
                                img=[hashtag['profile_pic_url']],
                                )
        yield from self.load_posts(response, hashtag)

    def load_posts(self, response, hashtag):
        # lazy loading extraction
        if hashtag['edge_hashtag_to_media']['page_info']['has_next_page']:
            query_variables = {"tag_name": hashtag['name'],
                               "first": 100,
                               "after": hashtag['edge_hashtag_to_media']['page_info']['end_cursor']}
            url = f'{self.pagination_url}?query_hash={self.query_hash["tags"]}&variables={json.dumps(query_variables)}'
            yield response.follow(url, callback=self.pagination_parse)
        # parse posts after pagination loading
        yield from self.post_parse(hashtag)

    def pagination_parse(self, response):
        # pagination parse
        yield from self.load_posts(response, response.json()['data']['hashtag'])

    @staticmethod
    def post_parse(edges):
        # parse of posts
        for edge in edges['edge_hashtag_to_media']['edges']:
            yield InstagramPostsItem(date_parse=datetime.now(),
                                     data=edge['node'],
                                     img=[edge['node']['display_url']],
                                     )

    @staticmethod
    def js_data_extract(response):
        # extract data from a java script
        script = response.xpath('//script[contains(text(), "window._sharedData =")]/text()').get()
        return json.loads(script.replace('window._sharedData =', '')[:-1])

    def user_parse(self, response):
        user_page = self.js_data_extract(response)['entry_data']['ProfilePage'][0]['graphql']['user']
        query_variables = {"id": user_page['id'],
                           "first": 100,
                           }
        yield from self.users_follow_parse(response, user_page, query_variables, follow_type='followings')
        yield from self.users_follow_parse(response, user_page, query_variables, follow_type='followers')

    def users_follow_parse(self, response, user_page, query_variables, follow_type):
        url = f'{self.pagination_url}?query_hash={self.query_hash[follow_type]}' \
              f'&variables={json.dumps(query_variables)}'
        yield response.follow(url, callback=self.followings_pagination_parse, cb_kwargs={'user_page': user_page,
                                                                                         'follow_type': follow_type,
                                                                                         })

    def followings_pagination_parse(self, response, user_page, follow_type):
        js_data = response.json()['data']['user'][self.follow_types[follow_type]]
        yield from self.follow_item(user_page, js_data['edges'], follow_type)
        if js_data['page_info']['has_next_page']:
            query_variables = {"id": user_page['id'],
                               "first": 100,
                               "after": js_data['page_info']['end_cursor'],
                               }
            yield from self.users_follow_parse(response, user_page, query_variables, follow_type)

    def follow_item(self, user_page, follow_users, follow_type):
        for user in follow_users:
            if follow_type == 'followings':
                yield InstagramUserFollowItems(user_id=user_page['id'],
                                               user_name=user_page['username'],
                                               follow_id=user['node']['id'],
                                               follow_name=user['node']['username'],
                                               )
            elif follow_type == 'followers':
                yield InstagramUserFollowItems(user_id=user['node']['id'],
                                               user_name=user['node']['username'],
                                               follow_id=user_page['id'],
                                               follow_name=user_page['username'],
                                               )
