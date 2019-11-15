"""
请求参数的md5验证类
"""


class AppMixin(object):

    def __init__(self):
        pass

    def check_sign(self):
        """验证签名"""
        return True
