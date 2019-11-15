"""
pymysql操作mysql
"""
import pymysql


class Mysql(object):
    def __init__(self, *args, **kwargs):
        print('**Mysql"{}'.format(kwargs))
        self.host = kwargs['host']  # ip
        self.database = kwargs['database']  # 数据库名字
        self.username = kwargs['username']  # 用户名
        self.password = kwargs['password']  # 用户密码
        self.connect_mysql()  # 在初始化的时候,就连接上数据库

    def connect_mysql(self):
        """连接数据库"""
        db = pymysql.connect(self.host, self.username, self.password, self.database)
        self.cursor = db.cursor()
        pass

    def select(self, sql):
        """查找"""
        self.cursor.execute(sql)
        result = self.cursor.fetchall()  # 取出所有的数据
        return result

    def add(self, sql):
        result = self.cursor.execute(sql)  # 返回受影响的行数
        return result

    def delete(self, sql):
        result = self.cursor.execute(sql)
        return result  # 返回受影响的行数

    def update(self):
        result = self.cursor.execute()
        return result  # 饭后受影响的行数

    def insert_into(self,sql):
        return self.cursor.execute(sql)  # 返回受影响的行数


def create_insert_sql(table_name, params):
    """准备插入sql语句"""
    sql_template = 'insert into {} ({}) values ({})'
    key = ','.join(['{}'.format(key) for key in params.keys()])
    value = ','.join(['{}'.format(params[value]) for value in params.keys()])
    return sql_template.format(table_name, key, value)


def create_update_sql(table_name, params, where):
    """准备跟新sql语句"""
    sql_template = 'update {} set {} where {}'
    update_str = ','.join(['{}={}'.format(key, params.get(key, '')) for key in params.keys()])
    return sql_template.format(table_name, update_str, where)


if __name__ == "__main__":
    from settings import db_condig
    # t = Mysql(db_config=db_condig['development'])
    # t.select('select * from dept_emp')
    test_params = dict(
        a=1,
        b=2,
        c=3
    )
    print(create_update_sql('orders', test_params, 'app_id=9087'))