"""
下订单扩展类
"""
import datetime
import functools
import settings
import time
import json
import hashlib
import copy

from utils.mysql import create_insert_sql, create_update_sql
from common.notify_url import NotifyUrl


class OrderMixin(object):

    def creating_orders_with_params(self, params, on_created):
        """在creating_orders预下单表中插入数据"""
        table_name = 'creating_orders'
        params = copy.deepcopy(params)
        params['created_at'] = datetime.datetime.now()
        params['user_id'] = self._app['user_id']  # TODO app 是从apps表中查出的
        params['app_id'] = self._app['id']
        params['platform_id'] = self._app['distributor_id']
        params['pay_platid'] = self._app['distributor_id']
        notify_url = params.pop('notify_url')  # 游戏通知url

        def _on_created(creating_order_sql, result, ex):
            if ex:
                print('**creating_order_with_params ERROR.sql_str:{}**'.format(creating_order_sql))
                on_created(None, ex)
            else:
                real_my_order_id = "%s%s%s" % (datetime.now().strftime("%Y%m%d%H%M%S"), result, int(time.time()))  # 拼接一个我们的自己订单号记录一下
                update_sql_str = create_update_sql(table_name, {'my_order_id':real_my_order_id}, 'id={}'.format(result))  # 跟新sql

                def my_order_id_updated(result, ex):
                    if ex:
                        print('**my_order_id_updated is Failed**')
                    else:
                        print('**my_order_id_updated is SUCCESS**')
                    on_created(real_my_order_id, None)
                    pass
                if params['my_order_id'].startswith('fake-'):  # TODO  这里面有一个逻辑，去判断订单号是不是要跟新
                    self._mysql.update(update_sql_str, callback=functools.partial(my_order_id_updated))
                else:
                    on_created(params['my_order_id'], None)
            pass

        def insert_creating_orders():
            """插入creating_orders表中"""
            creating_order_sql = create_insert_sql(table_name, params)
            self._mysql.insert(creating_order_sql, functools.partial(_on_created, creating_order_sql))
            pass

        if notify_url:
            notify_url_params = dict(
                app_id=self._app['id'], user_id=self._app['user_id'],
                url=notify_url, md5=hashlib.md5(notify_url).hexdigest(),
                created_at=datetime.datetime.now(), updated_at=datetime.datetime.now(), count=1
            )
            notify_url_sql = create_insert_sql(table_name, notify_url_params)
            data_cahe = dict(url=notify_url)

            def _on_upsert(result, ex):
                if not ex:
                    params['notify_url_id'] = result
                    insert_creating_orders()  # 往creating_orders 表中插入数据
                    NotifyUrl.instance().set(params['my_order_id'], data_cahe)  # 维护了一个缓存的字典，讲my_order_id于notify_url对应起来，这里面的数据在支付回调的时候会取出来的
                else:
                    print('**insert into notify_urls ERROR:sql_str:{}**'.format(notify_url_sql))
                pass
            # 插入notify_urls表中
            self._mysql.insert(notify_url, callback=_on_upsert)
        else:
            insert_creating_orders()

    def find_notify_url(self, notice_url_id, callback):
        """在数据库中查找notify_url"""
        if notice_url_id:
            return callback(None, None)
        sql_str = "select * from notify_urls where id={}".format(notice_url_id)

        def on_query(result, err):
            if err:
                print('**sql error**')
            result = result[0] if result else None
            callback(result, err)
        self._mysql.select(sql_str, callback=on_query)
        pass

    def save_order(self, order_info, on_saved, value_pairs):
        new_params = dict(
            app_id=self._app_id,user_id=order_info['role_id'], my_order_id=order_info['game_order'],
            platform_id=order_info['plat_id'], theirs_order_id=order_info['plat_order'],
            order_status = settings.SUCCESS, notifying_status=settings.NOTIFYING, created_at = datetime.datetime.now()
        )
        update_temp_info = dict(
            my_order_id = new_params['my_order_id'],
            app_id =new_params['app_id']
        )
        new_params.update(value_pairs)
        # 准备插入orders中的sql语句
        sql_str = create_insert_sql(settings.ORDERS_NAME, new_params)

        def callback(created_at, result, ex):
            if ex:
                print('**保存订单orders出错了**')
            else:
                on_saved(created_at, result, ex)
        self._mysql.insert(sql_str, functools.partial(callback, new_params['created_at']))

    def create_order_sign(self):
        """部分渠下单需要签名"""
        return ''

    def _send_order(self, order_info):
        """正式通知游戏服务器发货"""
        send_info = self.create_send_order_info(order_info)

        def on_saved(created_at, result, ex):
            if ex or not result:
                print('**save order error, order_info:{}**'.format(order_info))
            """
            created_time:订单成功存库时间，这个时间必须发送到数据中心，以便查单和对账
            order_info：原始创单信息，主要用于推送，以便获取数据中心需要的部分字段信息
            rep_num：重复通知游戏服次数，默认是3次，主要为了防止网络短暂性波动故障
            send_data：是否发送订单到数据中心,主要是为了补单时订单不存在的情况，需要推送订单
            """
            send_data = True
            kwargs =dict(app=self._app_id, created_at=created_at, order_info=order_info, rep_num=3, send_data=send_data)
            # 通知游戏服务器发货
            self.game_server.send(send_info, **kwargs)
            # IOLoop.current().call_later()  TODO 后续补上重发的逻辑
            pass
        if send_info.get('gitfcoin', 0):
           value_pairs = {'giftcoin':order_info.get('giftcoin'), 'ideal_price':order_info.get('ideal_price'), 'real_price':order_info.get('real_price')}
        else:
           value_pairs = {'verified': 1}
        # 保存订单于正式订单表里面
        self.save_order(send_info, on_saved, value_pairs)

    def save_tj_data(self, app_id, my_order_id, send_data):
        """将未发送成功到数据中心的订单记录到 app_id, my_order_id, send_data"""
        data = {
            "daynum": int(time.strftime("%Y%m%d", time.localtime())),
            "app_id": app_id,
            "my_order_id": my_order_id,
            "send_data": json.dumps(send_data),
            "status": 0
        }
        sql_str = create_insert_sql('tj_records', data)

        def callback(result, ex):
            if ex:
                print('tj_records save success')
            else:
                print('tj_records save failed')
            pass
        self._mysql.insert(sql_str, callback=callback)

    def create_send_order_info(self, order_info):
        send_info = {}
        send_info['app_id'] = self._app_id  #游戏id
        send_info['server_id'] = ''  # 游戏服务器id
        send_info['plat_id'] = int(order_info.get("plat_id", 0)) or int(order_info.get('pay_platid', 0)) or int(order_info.get('platform_id', 0)) # 渠道id
        send_info['accid'] = order_info['account']
        send_info['myaccid'] = order_info['game_account_id']
        send_info['plat_order'] = order_info.get('theirs_order_id', 'my_order_id')
        send_info['game_order'] = order_info['my_order_id']
        send_info['role_id'] = order_info['role_id']
        send_info['amount'] = order_info['amount']+order_info.get('giftcoin', 0) or order_info['real_price']
        send_info['goods_id'] =order_info.get('item_id', 0)
        send_info['ext'] = order_info.get('ext', '')
        send_info['notify_url_id'] = order_info.get('notify_url_id', 0)
        return send_info

    def send_order(self, tmp_info, giftcoin=0):
        """通知游戏服务器发货,giftcoin:代金券"""
        my_order_id = tmp_info.get('my_order_id', '')

        def callback(order_info, result, error):
            if error or not result:
                print('**order:{} not exist in creating_orders**'.format(my_order_id))
                # 订单发送失败，可以保存下来以便再次发送
                self.save_notify_order(order_info)
            # 在进行金额校验
            elif order_info['amount'] +float(giftcoin) < order_info['real_price']:
                print('**the order amount cant match to the creating_orders**')
                return
            else:
                order_info = result[0]
                order_info.update(tmp_info)
                order_info['giftcoin'] =float(giftcoin)
                self._send_order(order_info)
        self.is_creating_order_exist(my_order_id, functools.partial(callback, tmp_info))

    def save_notify_order(self, order_info):
        """某些订单发送失败，保存起来以便下次发送"""
        pass

    def is_creating_order_exist(self, my_order_id, callback):
        table_name = settings.CREATING_ORDERS_NAME  # creating_orders
        sql_str = "select from {} where app_id={} and my_order_id={};".format(table_name, self._app_id, my_order_id)
        # 执行sql
        self._mysql.select(sql_str, callback=callback)

    def is_order_exist(self, my_order_id, callback):
        """my_order_id 是否存在于creating_orders表中"""
        # TODO 数据库查询操作暂且不做
        callback(0, None)

if __name__ =="__main__":
    pass