"""
单线程的去维护 notify_url
"""
from utils.cache import CacheMixin


class NotifyUrl(CacheMixin):
    is_instance = None

    def __new__(cls, *args, **kwargs):
        if not cls.is_instance:
            cls.is_instance = super(NotifyUrl, cls).__new__(cls, *args, **kwargs)
        return cls.is_instance

    @classmethod
    def instance(cls):
        if cls.is_instance is None:
            NotifyUrl()
        return cls.is_instance


if __name__ == "__main__":
    test01 = NotifyUrl()
    test02 = NotifyUrl()

    print(id(test01))
    print(id(test02))

