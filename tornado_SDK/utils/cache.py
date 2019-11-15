"""
维护一个缓存字典， 来保存notify_url
"""


class CacheMixin(object):
    _cache = dict()

    def set(self, key, value):
        """往字典里面设置一个值"""
        self.__class__._cache[key] = value

    def get(self, key):
        """从字典里面取出一个值"""
        return self.__class__._cache[key]

    def delete(self, key):
        """释放内存中的资源"""
        del self.__class__._cache[key]


if __name__ == "__main__":
    pass
