"""
此为推送数据到服务中心
"""
import urllib.parse
import time
import base64
import json

from common.notify_url import NotifyUrl
from utils.order_mixin import OrderMixin
from utils.sign_mixin import SignMixin
from utils.http_mixin import HttpMixin
from tornado.httputil import url_concat
from tornado.ioloop import IOLoop


class ZQWebGateway(OrderMixin, SignMixin, HttpMixin):
    """推送订单信息到数据中心"""
    DATA_CENTER_URL = 'http://tj.zqgame.com/ZqPay'  # TODO 此url还没有弄清楚呢

    def __init__(self, *args, **kwargs):
        self._mysql = kwargs['mysql']

    def send(self, send_info, **kwargs):
        app_id, my_order_id = int(kwargs['app_id']), send_info['my_order_id']
        data_cahe = NotifyUrl.instance().get(my_order_id)  # 取出缓存在字典里面的notify_url,notify_url是在创建订单的时候存入进去的，有格式
        pay_notice_url = data_cahe['url'] if data_cahe else None

        def _on_http_response(user_data, res):
            succeed = False
            game_order, plat_order = send_info.get('game_order', ''), send_info.get('plat_order', '')

            if (not res.error) and str(res.body).strip() == '200':
                succeed = True
                NotifyUrl.instance().delete(my_order_id)  # 从缓存中删除
                # TODO 跟新数据库里面的数据，orders
                # 推送订单到数据中心
                self.send_order_to_data_center(kwargs['order_info'], kwargs['created_at'], succeed,
                                               save_func=self.save_tj_data)

            if not succeed:
                # TODO 不成功，触发重发机制，此功能后续在写
                pass

        def on_notice(result, error):
            params = {}
            keys = ['plat_id', 'game_order', 'plat_order', 'amount', 'server_id', 'role_id', 'ext']
            for key in keys:
                params[key] = send_info.get(key, '')

            params['amount'] = '%0.2f' % (float(send_info['amount']))
            params['sign'] = self.send_order_sign(params)
            # url = self._app['pay_notice_url'] if (err or not result) else result['url']
            url = ''  # TODO url从里面进行选择
            url = urllib.parse.quote(url)
            user_data = {'url': url_concat(url, params)}
            # 发送请求
            self.request_get(url, params=params, callback=_on_http_response, user_date=user_data)

        if pay_notice_url is None:
            self.find_notify_url(send_info['notify_url_id'], on_notice)
        else:
            pass

    def send_order_to_data_center(self, order_info, created_time, order_status, send_date=None, repeat_num=3,
                                  save_func=None):
        """推送订单到数据中心"""
        if send_date:
            data = send_date
        else:
            data = {
                'act_gold': 'unknown',
                'act_adcode': 'unknown',
                'act_cp_id': '1',
                'act_role_level': 'unknown',
                'act_vip_level': 'unknown',
                'act_client_server': '2',
                'act_local_ip': 'unknown',
                'act_time': str(int(time.mktime(time.strptime(created_time, "%Y-%m-%d %H:%M:%S"))) * 1000),
                'act_platform_id': order_info.get('platform_id', 0),
                'act_account_id': order_info.get('account', order_info.get('game_account_id', 'unknown')),
                'act_game_id': order_info.get('app_id', 'unknown'),
                'act_server_id': order_info.get('server_id', 'unknown'),
                'act_role_id': order_info.get('role_id', 'unknown'),
                'act_plat_order': order_info.get('theirs_order_id', order_info['my_order_id']),
                'act_game_order': order_info['my_order_id'],
                'act_goods_id': order_info.get('item_id', 'unknown'),
                'act_amount': str(int(float(order_info.get('real_price', '0')))),
                'act_order_status': '1' if order_status else '0',
            }
        body = "data={}".format(base64.b64encode(json.dumps(data)))
        user_data = dict(order_info=order_info, data=data, order_status=order_status, repeat_num=repeat_num,
                         created_time=created_time)

        # 发送请求， 推送订单到数据中心

        def _on_http_response(user_data, res):
            order_info, data, repeat_num = user_data['order_info'], user_data['data'], user_data['repeat_num']
            order_status = user_data['order_status'], created_time = user_data['created_time']
            if not res.error:
                print('**The order send to data center success:{}**'.format(str(user_data)))
            # 开启重发三次
            else:
                if repeat_num == 0:
                    print('**Finally send Filed , the order info:{},data:{}**'.format(order_info, data))
                    # 保存数据库，方便查询重发
                    self.save_tj_data(data['act_game_id'], data['act_game_order'], data)
                else:
                    repeat_num -= 1
                    print('**The order send to data center failed, repeat send order:Time={}**'.format(repeat_num))
                    # 延迟15秒继续执行
                    IOLoop.instance().call_later(15, self.send_order_to_data_center(order_info, created_time, order_status, data, repeat_num))

        self.request_post(self.DATA_CENTER_URL, body, user_data=user_data, callback=_on_http_response)


if __name__ == "__main__":
    pass
