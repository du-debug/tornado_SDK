"""
公共的create_order
下订单类
"""
import functools
import time

from utils.order_mixin import OrderMixin


class CreateOrderStub(OrderMixin):
    """default create_order"""
    keys = ('account', 'accid', 'session', 'game_order', 'amount', 'notice_url', 'server_id',
            'role_id', 'role_name', 'goods_id', 'goods_name', 'goods_desc', 'ext', 'sign')

    def __init__(self):
        pass

    def create_order_result(self, packet, callback, order_info={}, succeed=True, desc=''):
        if succeed:
            packet['notice_url'] = order_info.get('notice_url') or self.get_pay_notice_url(self._app, int(
                self._platform_info['distributor_id']))
            packet['create_time'] = packet.get("create_time") or order_info.get("create_time") or time.strftime(
                "%Y%m%d%H%M%S", time.localtime())
            packet['plat_order'] = order_info.get("plat_order", "")
            # 加上签名
            if order_info.get('sign'):
                self.log_info('sign:%s' % order_info.get('sign'))
                packet['sign'] = order_info.get('sign')
            else:
                packet['sign'] = self.create_order_sign(packet)
            callback(packet, succeed)
        else:
            callback(packet, succeed)

    def create_plat_order(self, packet, callback):
        self.create_order_result(packet, callback, {}, succeed=True)

    def on_create_order(self, packet, callback, result, ex):
        """
        预下单表创建回调函数
        result:my_order_id, real_my_order_id
        ex:None
        """
        if ex:
            print("**下单失败。{}**".format(ex))
            self.create_order_result(packet, callback, {}, succeed=False, desc='系统异常')
        else:
            self.create_plat_order(packet, callback)

    def create_order(self, packet, callback):
        # 准备参数
        params = dict(
            my_order_id=packet.get('game_order'), server_id=packet.get('server_id', 0),
            game_account_id=packet.get('myaccid', 0), role_id=packet['role_id'], ext=packet.get('ext', ''),
            notify_url=packet.get('notice_url'), ideal_price=packet['amount'], account=packet['accid'],
            real_price=packet['amount'], item_id=packet['goods_id'], role_name=packet['role_name']
        )
        # 在预下单表中插入订单信息
        self.creating_orders_with_params(params, functools.partial(self.on_create_order, packet, callback))

    def process(self, request_handler, params):
        """入口 函数"""
        # TODO  如果没有订单号，则自己生成一个订单号，此逻辑后面实现
        self.create_order(params, request_handler.on_create_order_callback)
        pass

    def get_params_keys(self):
        return CreateOrderStub.keys


if __name__ == "__main__":
    # 测试url
    test_url = 'http://127.0.0.1:8080/0/create_order/test?order_id=dwh&my_order_id=18&real_price=15'
    pass
