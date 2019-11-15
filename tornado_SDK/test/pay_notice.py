"""
支付回调通知
"""
from utils.order_mixin import OrderMixin
from utils.sign_mixin import SignMixin


class PayNotice(OrderMixin, SignMixin):
    keys = ('my_order_id', 'theirs_order_id', 'price')

    def __init__(self):
        pass

    def is_order_success(self, params):
        return True

    def process(self, request_handler, params):
        request_handler.write('OK')
        request_handler.finish()
        print('**params:{}**'.format(params.get('text_params')))
        params = params.get('text_params') if params.get('text_params', None) else ''
        my_order_id, theirs_order_id, price= params.get('my_order_id'), params.get('theirs_order_id'), float(params['price']) * 100

        def on_exist(result, ex):
            if result == 0:
                order_info = {
                    'my_order_id': my_order_id,
                    'amount': price,
                    'theirs_order_id': params['theirs_order_id']
                }
                print('**send_order_info:{}**'.format(order_info))
            else:
                print('**order is exist。my_order_id:{}, theirs_order_id:{}**'.format(my_order_id, theirs_order_id))
        if self.is_order_success(params):
            self.is_order_exist(my_order_id, on_exist)
        return True

    def get_params_keys(self):
        return PayNotice.keys


if __name__ == '__main__':
    pass
