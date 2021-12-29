import json
import re
from copy import deepcopy
from urllib.parse import urlencode

import scrapy
from scrapy.http import HtmlResponse

from instagramparser.items import InstagramProfileItem, InstagramUser2FollowerItem


def fetch_csrf_token(text):
    matched = re.search(f'"csrf_token":"\w+"', text).group()
    return matched.split(':').pop().replace(r'"', '')


def fetch_user_id(text, username):
    matched = re.search(f'"id":"\d+","username":"{username}"', text).group()
    return int(json.loads('{' + matched + '}').get('id'))


def fetch_private_user_id(text):
    matched = re.findall(f'"id":"\d+"', text)[-1]
    return int(matched.split('"')[-2])


def fetch_user_img(text):
    matched = re.findall(f'"profile_pic_url_hd":"[^"]+"', text)[-1]
    return matched.split('"')[-2].replace('\\u0026', '&')


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']

    instagram_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    instagram_login = 'vexoel'
    instagram_password = '#PWD_INSTAGRAM_BROWSER:10:1640250406:AXtQAD85qJuMDe/TNdIFs55vkubffrDp2j3sD3drRchjHDtoXi/GSnIpTneKSBjWHgATGhg1q18qNJD2PKYgJ+xhnj0Kxr2tDMDnaK16LifaVX7mgDA208UMOTTTYfz2VFNJn0qyMBbA0TcKU1obRNLDVA=='

    instagram_api = 'https://i.instagram.com/api/v1/'
    instagram_api_headers = {'User-Agent': 'Instagram 155.0.0.37.107'}

    def __init__(self, users, **kwargs):
        super().__init__(**kwargs)
        self.users = users

    def parse(self, response: HtmlResponse):
        csrf = fetch_csrf_token(response.text)

        yield scrapy.FormRequest(self.instagram_login_link,
                                 method='POST',
                                 callback=self.login,
                                 formdata={'username': self.instagram_login,
                                           'enc_password': self.instagram_password},
                                 headers={'X-CSRFToken': csrf})

    def login(self, response: HtmlResponse):
        j_data = response.json()

        if j_data.get('authenticated'):
            for user in self.users:
                yield response.follow(f'/{user}',
                                      callback=self.user_parse,
                                      cb_kwargs={'user_id': None,
                                                 'user_name': user,
                                                 'need_follows': 1})

    def user_parse(self, response: HtmlResponse, user_id, user_name, need_follows):
        if not user_id:
            try:
                user_id = fetch_user_id(response.text, user_name)
            except:
                user_id = fetch_private_user_id(response.text)

        user_img = fetch_user_img(response.text)

        if need_follows == 1:
            variables = {'count': 12, 'search_surface': 'follow_list_page'}

            url_followers = f'{self.instagram_api}friendships/{user_id}/followers/?{urlencode(variables)}'

            yield response.follow(url_followers,
                                  callback=self.user_followers_parse,
                                  cb_kwargs={'user_id': user_id,
                                             'variables': deepcopy(variables)},
                                  headers=self.instagram_api_headers)

            variables = {'count': 12}

            url_following = f'{self.instagram_api}friendships/{user_id}/following/?{urlencode(variables)}'

            yield response.follow(url_following,
                                  callback=self.user_following_parse,
                                  cb_kwargs={'user_id': user_id,
                                             'variables': deepcopy(variables)},
                                  headers=self.instagram_api_headers)

        yield InstagramProfileItem(user_id=user_id, user_name=user_name, user_img=user_img)

    def user_followers_parse(self, response: HtmlResponse, user_id, variables):
        j_data = response.json()

        max_id = j_data.get('next_max_id')

        if max_id:
            variables['max_id'] = max_id

            url_followers = f'{self.instagram_api}friendships/{user_id}/followers/?{urlencode(variables)}'

            yield response.follow(url_followers,
                                  callback=self.user_followers_parse,
                                  cb_kwargs={'user_id': user_id,
                                             'variables': deepcopy(variables)},
                                  headers=self.instagram_api_headers)

        for follower in j_data.get('users'):
            follower_id = follower.get('pk')
            follower_name = follower.get('username')

            yield InstagramUser2FollowerItem(user_id=user_id, follower_id=follower_id)

            yield response.follow(f"/{follower_name}",
                                  callback=self.user_parse,
                                  cb_kwargs={'user_id': follower_id,
                                             'user_name': follower_name,
                                             'need_follows': 0})

    def user_following_parse(self, response: HtmlResponse, user_id, variables):
        j_data = response.json()

        max_id = j_data.get('next_max_id')

        if max_id:
            variables['max_id'] = max_id

            url_following = f'{self.instagram_api}friendships/{user_id}/following/?{urlencode(variables)}'

            yield response.follow(url_following,
                                  callback=self.user_following_parse,
                                  cb_kwargs={'user_id': user_id,
                                             'variables': deepcopy(variables)},
                                  headers=self.instagram_api_headers)

        for following in j_data.get('users'):
            following_id = following.get('pk')
            following_name = following.get('username')

            yield InstagramUser2FollowerItem(user_id=following_id, follower_id=user_id)

            yield response.follow(f"/{following_name}",
                                  callback=self.user_parse,
                                  cb_kwargs={'user_id': following_id,
                                             'user_name': following_name,
                                             'need_follows': 0})
