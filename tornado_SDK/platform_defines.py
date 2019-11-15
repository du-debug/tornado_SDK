"""
对应的各个服务表示
"""
from tornado.util import import_object

ePlatform_TEST = 0  # 测试

__name_to_id = dict(
    test=ePlatform_TEST
)

__actives__ = ['test']

# 字典包含了各个模块的以及所包含的文件
__platform_id_to_handler__ = {}


def name_to_id(name):
    return __name_to_id.get(name, None)


def import_defines():
    for p in __actives__:
        pm = import_object(p)
        __platform_id_to_handler__[name_to_id(p)] = getattr(pm, 'get_handlers')()  # 讲各个模块的文件放到字典里面


def get_platform_by_id(id):
    return __platform_id_to_handler__.get(id)


if __name__ == "__main__":
    import_defines()
    print(get_platform_by_id(0))
