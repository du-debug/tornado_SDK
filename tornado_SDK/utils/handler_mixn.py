"""
handler_mixin:公共处理分发
"""
import platform_defines


class HandlerMixin(object):

    def handle_request_with_process(self, app_id, handler_name,  action):
        """处理app_id, action,寻找相对于的模块"""
        app_id, handler_name, action = int(app_id), handler_name,  action
        handler = None
        print(app_id, handler_name, action)
        self._app_id = app_id  # TODO 先用app_Id 代替数据库查询结果
        # 如果这个方法在这个字典里面
        handlers = platform_defines.get_platform_by_id(app_id)
        if handler_name in handlers:
            handler = handlers[handler_name]()  # 找到action对应的类并进行初始化
            print(handler)
        else:
            print("handler 没有在 字典里面")
        self.on_find_handler(handler)

    def collect_params(self, keys):
        """从请求中获取参数"""
        text_params = {}
        for key in keys:
            p = self.get_argument(key, None)
            if p:
                text_params[key] = p
        # 获取传递过来的数据
        file_params = self.request.files
        if file_params:
           packet = dict(text_params=text_params, file_params=file_params)
        else:
            packet = dict(text_params=text_params)
        return packet

    def on_find_handler(self, handler):
        """分发到各自的类中执行各自的方法"""
        handler_by_flag = False
        if handler is not None:
            if hasattr(handler, 'get_params_keys'):
                packet = self.collect_params(handler.get_params_keys())  # 取出请求体中数据
                print('**on_find_handler packet:{}**'.format(packet))
            print('测试{}'.format(handler))
            checked = self.check_sign(packet) if hasattr(self, 'check_sign') else handler.check_sign(packet)
            print('**Checked:{}**'.format(checked))
            if handler.process(self, packet) and checked:  # 对请求参数的md5校验
                handler_by_flag = True
                print('**checked True**')
        if not handler_by_flag:
            print("sign not math")
            self.finish()


if __name__ == "__main__":
    platform_defines.import_defines()
    print(platform_defines.__platform_id_to_handler__)
    print(platform_defines.get_platform_by_id(0))
