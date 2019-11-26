"""
菜品识别
"""
import json
import base64
import requests

from . import config
from utils.http_mixin import HttpMixin
from functools import partial
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from urllib import parse


class VegetableKnow(HttpMixin):
    keys = ()

    def __init__(self):
        pass

    def process(self, request_handler, params):
        self.get_access_token(params, request_handler, self.on_vegetable_know_callback)
        return True

    def on_vegetable_know_callback(self):
        pass

    def get_access_token(self, params, request_handler, callback):
        """获取access_token，有效期为30天"""
        packet = {
            "grant_type": "client_credentials",
            "client_id": config.app_key,
            "client_secret": config.app_secret_key
        }
        self.request_get(config.vegetable_know_get_access_token_url, params=packet, user_date=callback, callback=partial(self.on_access_token, params))

    def on_access_token(self, params, callback, res):
        print('**on_access_token:{},{}**'.format(params, callback))
        ret = json.loads(res.body)
        # 取出access_token的值
        access_token = ret.get('access_token', '')
        if access_token:
            self.vegetable_know(access_token, params)

    def vegetable_know(self, access_token, params):
        img = base64.b64encode(params.get('file_params', '').get("image", "")[0].get("body", ""))
        print("image:{}".format(img))
        params = {"image": img}
        request_url = config.vegetable_know_url + "?access_token=" + access_token
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        response = requests.post(request_url, data=params, headers=headers)
        if response:
            print('**response:{}**'.format(response.json()))


    def on_vegetable_know(self, res):
        print('**on_vegetable_knoe:{}**'.format(res))
        # print(json.loads(res.body))
        pass

    def get_params_keys(self):
        return VegetableKnow.keys


if __name__ == '__main__':
    pass