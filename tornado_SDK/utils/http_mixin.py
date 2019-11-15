"""
tornado — http_client
"""
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from urllib.parse import urlencode
from functools import partial
from tornado.ioloop import IOLoop


class HttpMixin(object):

    def request_get(self, url, params=None, user_date=None, callback=None, headers=None):
        """发送get请求"""
        client = AsyncHTTPClient()
        if params:
            url = url + '?' + urlencode(params)
        if headers:
            http_request = HTTPRequest(url, method='GET', headers=headers, connect_timeout=20, validate_cert=False)
        else:
            http_request = HTTPRequest(url, method='GET', connect_timeout=20, validate_cert=False)
        client.fetch(http_request, partial(callback, user_date))

    def request_post(self, url, body, params=None, user_data=None, callback=None, headers=None):
        """发送post请求"""
        client = AsyncHTTPClient()
        if params:
            url = url + '?' + urlencode(params)
        if headers:
            http_request = HTTPRequest(url, method='POST', body=body, headers=headers, connect_timeout=20, validate_cert=False)
        else:
            http_request = HTTPRequest(url, method='POST', body=body, connect_timeout=20, validate_cert=False)
        client.fetch(http_request, partial(callback, user_data))


if __name__ == "__main__":
    # 测试
    test = HttpMixin()

    def callback(user_date, res):
        print(res.body)
    test.request_get('https://www.baidu.com', callback=callback)
    IOLoop.current().start()