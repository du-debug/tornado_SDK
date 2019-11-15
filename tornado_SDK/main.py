"""
后台统一提供数据
"""
import tornado.web
import tornado.httpserver
import tornado.ioloop
from tornado.options import options

import settings
import platform_defines
from utils.handler_mixn import HandlerMixin
from utils.async_mysql import AsyncMysql
from utils.sign_mixin import SignMixin
from game_server import ZQWebGateway


class Web(tornado.web.RequestHandler, HandlerMixin):
    """通用web类"""

    def initialize(self, mysql, game_server):
        self._mysql = mysql  # 数据库对象引用
        self.game_server = game_server
        pass

    @tornado.web.asynchronous
    def get(self, app_id, handler_name,  action):
        """处理get请求"""
        print('**打印日志信息:post_url:{}, body:{}**'.format(self.request.uri, self.request.body))
        self.handle_request_with_process(app_id, handler_name, action)

    @tornado.web.asynchronous
    def post(self, app_id, handler_name, action):
        """处理post请求"""
        print('**打印日志信息:post_url:{}, body:{}**'.format(self.request.uri, self.request.body))
        self.handle_request_with_process(app_id, handler_name, action)


class Voice(Web, SignMixin):
    """语音识别"""

    def on_voice_callback(self, packet, msg):
        """返回回调"""
        data = {'status':200, 'data': packet} if msg else {'status':403, 'data':packet}
        self.write(data)
        self.finish()


class CreateOrder(Web, SignMixin):
    """下单"""

    def on_create_order_callback(self, succeed, msg):
        """订单回调"""
        data ={'status':200, 'data':succeed} if succeed else {'status':403, 'data':msg}
        self.write(data)
        self.finish()


class LevelUpdate(Web, SignMixin):
    """等级更新接口"""
    def on_level_update_callback(self):
        pass

    def check_sign(self, packet):
        """md5校验登录参数"""
        return packet['sign'] == self.check_sign(packet)


def start():
    # 导入数据大字典
    platform_defines.import_defines()
    try:
        tornado.options.parse_command_line()
        # 初始化数据库
        mysql = AsyncMysql(db_config=settings.db_condig['development'])
        # 初始化游戏服务器
        game_server_params = settings.game_server_config[options.mode]
        game_server = ZQWebGateway(game_server_params['host'], game_server_params['port'], mysql=mysql)
        app = tornado.web.Application([
            # 以下几个是公共接口
            (r'/(?P<app_id>[^/]+)/(?P<handler_name>[^/]+)/(?P<action>[^/]+)', CreateOrder, dict(mysql=mysql, game_server=game_server)),  # 百度语音访问
            # 以下是特殊接口
            (r'/(?P<app_id>[^/]+)/(?P<handler_name>[^/]+)/(?P<action>voice_translate)', Voice, dict(mysql=mysql, game_server=game_server)),  # 百度语音访问
            (r'/(?P<app_id>[^/]+)/(?P<handler_name>[^/]+)/(?P<action>level_update)', LevelUpdate, dict(mysql=mysql, game_server=game_server)),  # 等级更新接口
        ])
        http_server = tornado.httpserver.HTTPServer(app)
        http_server.listen(options.port, options.address)
        tornado.ioloop.IOLoop.current().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.instance().stop()
    except Exception as e:
        """此异常先不处理，直接抛出"""
        print(e)
        raise


def main():
    """入口函数"""
    # 定义一些全局变量
    options.define(name='port', default=settings.PORT, help='run on the give port', type=int)  # 服务器端口
    options.define(name='address', default=settings.HOST, help='run on give on address', type=str)  # 服务器地址
    options.define(name='mode', default='development', help='default run in development mode')  # 运行模式
    start()


if __name__ == "__main__":
    main()
    # 多线程数据库已经写好，后面的一些参数可以存在数据库中
    # 测试url:127.0.0.1:8080/0/level_update/level_update?name=dwh&age=18
    # 测试url:127.0.0.1:8080/0/pay_notice/test?my_order_id=152&theirs_order_id=520&price=1000
