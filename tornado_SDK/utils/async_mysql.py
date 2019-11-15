"""
异步多线程数据库
此模块为项目初始化mysql模块，并由此进入多线程具体的执行sql语句
"""
from utils.async_mixin import async_class, AsyncMixin, WorkThread
from utils.mysql import Mysql


class MsqlThread(WorkThread):

    def __init__(self, *args, **kwargs):
        print('**MysqlThread:{}**'.format(kwargs))
        self._mysql = Mysql(**kwargs['db_config'])  # 初始化数据库
        super(MsqlThread, self).__init__(*args, **kwargs)  # 也初始化父类

    def get_handler(self):
        """用来返回数据库实例"""
        return self._mysql

@async_class
class AsyncMysql(AsyncMixin):
    __async_methods__ = ('select', 'add', 'delete', 'update')

    def __init__(self, db_config=None, **kwargs):
        kwargs['thread_klass'] = MsqlThread  # 将数据库类的引用存进kwargs里面中
        kwargs['thread_klass_args'] = dict(db_config=db_config, pool=self)
        super(AsyncMysql, self).__init__(**kwargs)

    def select(self, sql, callback=None):
        """查"""
        return sql

    def add(self, sql, callback=None):
        """增加"""
        return sql

    def delete(self, sql, callback=None):
        """删除"""
        return sql

    def update(self, sql, callbacl=None):
        """更新"""
        return sql


if __name__ == '__main__':

    from settings import db_condig

    test = AsyncMysql(db_config=db_condig['development'])  # 测试
    sql = 'select * from dept_emp'

    def callback(result):
        print(result)
    test.select(sql, callback=callback)