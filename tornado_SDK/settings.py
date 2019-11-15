"""
配置参数
"""
import os
import sys

PATH_FILE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PATH_FILE)

HOST = '127.0.0.1'  # 服务器host地址
PORT = 8080  # 服务器端口

db_condig = dict(
    development=dict(
        host='localhost',
        password='dwh19940912-',
        database='db_test',
        username='root'
    ),
    production=dict()
)

# 预下单表名称
CREATING_ORDERS_NAME = "creating_orders"
# 正式下单表
ORDERS_NAME = "orders"
# 渠道表
DISTRIBUTION_INFOS_NAME = "distribution_infos"
# 应用表
APPS_NAME = "apps"

# 订单状态
SUCCESS = 1
NOTIFYING = 4 # 通知状态

"""
游戏服务的配置
"""
game_server_config = dict(
    development=dict(
        host='',
        port=''
    ),
    production=dict(
        host='',
        port=''
    )
)
