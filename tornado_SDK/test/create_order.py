"""
test create_order
"""
from common.create_order_stub import CreateOrderStub
from .app_mixin import AppMixin


class CreateOrder(CreateOrderStub, AppMixin):
    """create——order 为各个模块独特的下订单方式"""
    keys = ('name', 'age')

    def __init__(self):
        pass

    def process(self, request_handler, packet):
        print(packet, request_handler)
        return True

    def get_params_keys(self):
        return CreateOrder.keys