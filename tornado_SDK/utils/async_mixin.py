"""
async_mysql的中间类在此和一些方法
"""
import os
import sys

# PATH_FILE = os.path.dirname(os.path.abspath(__file__))
# sys.path.insert(0, PATH_FILE)
import threading
from functools import wraps, partial
from queue import Queue


class WorkThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self)
        print('**WorkThread:{}**'.format(kwargs))
        # self._name = kwargs['name']
        self.poll= kwargs['pool']  # 取出队列
        self.running = True

    def run(self):
        while self.running:
            (func, callback)=self.poll.queue.get()  # 取出func, callback
            handler = self.get_handler()  # 得到数据库实例引用
            if hasattr(handler, func.func.__name__):
                data = func()
                # 执行sql语句
                result = getattr(handler, func.func.__name__)(data)
                # 回调callback，执行
                callback(result)


class AsyncMixin(object):
    def __init__(self,
                 thread_klass=None,
                 thread_klass_args=None,
                 num_thread=10):
        self.queue = Queue()  # 初始化队列
        print('**thread_class:{},thread_klass_args:{}**'.format(thread_klass, thread_klass_args))

        # 开启线程
        for num in range(num_thread):
            thread_klass_args['name'] = 'thread_%d' % ( num)
            print('**Thread_name:thread_%s**' % (num) )
            t = thread_klass(**thread_klass_args)  # 初始化数据库
            t.start()  # 开启多线程执行sql

    def add_task(self, func, callback=None):
        self.queue.put((func, callback))


def async_thread(func):
    @wraps(func)
    def add_method_queue(*args, **kwargs):
        print(dir(args[0]))  # 为 AsyncMsql类的引用
        obj = args[0]
        if isinstance(obj, AsyncMixin):
            if 'callback' in kwargs:
                obj.add_task(partial(func, *args, **kwargs), kwargs['callback'])  # 将其添加到队列中
    return add_method_queue


def async_class(klass):
    if hasattr(klass, '__async_methods__'):
        __async_methods__ = getattr(klass, '__async_methods__')
        print('**async_class  __async_methods__: {}**'.format(__async_methods__))
        for name in __async_methods__:
            method = getattr(klass, name)
            setattr(klass, name, async_thread(method))  # 这里会赋给一个新的引用
    return klass


if __name__ == "__main__":
    pass