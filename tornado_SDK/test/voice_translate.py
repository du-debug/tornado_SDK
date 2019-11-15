"""
test
voice_translate
"""
import json
import os
import base64
from utils.http_mixin import HttpMixin
from functools import partial

from . import config
from .app_mixin import AppMixin


class VoiceTranslate(HttpMixin, AppMixin):
    keys = ('name', 'age')  # 从前端穿过的请求中取参数的键的名字

    def process(self, request_handler, packet):
        """分发到各模块的方法入口"""
        print('**参数是:{}, class:{}**'.format(packet, request_handler))
        # 处理具体逻辑，想百度ai发起请求
        params = dict(
            grant_type="client_credentials",
            client_id=config.app_key,
            client_secret=config.app_secret_key
        )
        # 发起请求, 获取access_token
        packet['on_voice_callback'] = request_handler.on_voice_callback
        self.request_get(config.get_access_token_url, params=params, callback=partial(self.on_access_token), user_date=packet)
        return True

    def on_access_token(self, packet, res):
        print('**on_access_token body:{}**'.format(res.body))
        ret = json.loads(res.body)
        # 取出access_token的值
        access_token = ret.get('access_token', '')
        if access_token:
            # 完成语音转义
            self.translate_from_voice(packet, access_token)

    def translate_from_voice(self, packet, access_token):
        print('**translate_from_voice packet:{}, access_token:{}**'.format(packet, access_token))
        file_params = packet.get('file_params', '')
        file_bytes = file_params.get('file', '')[0].get('body')  # 拿到文件的二进制数据
        if file_bytes:
            # 准备参数
            params = dict(
                format='amr',  # 语音文件的格式，推荐pcm
                rate=16000,  # 固定值
                dev_pid=1537,  # 普通话输入模型
                channel=1,  # 固定值
                token=access_token,  # access_token
                cuid='00-FF-B2-AA-33-F1',  # 用户唯一表示,使用的是本机mac地址
                len=len(file_bytes),
                speech=base64.b64encode(file_bytes).decode('utf8'),  # 地语音文件的的二进制语音数据 ，需要进行base64 编码
            )
            headers = {'Content-Type': 'application/json'}  # 请求头人家已经规定好了
            self.request_post(config.get_voice_url, json.dumps(params), user_data=packet, callback=self.on_translate_from_voice, headers=headers)

    def on_translate_from_voice(self, new_packet, res):
        print('**on_translate_from_voice body:{}, params:{}**'.format(res.body, new_packet))
        ret = json.loads(res.body)
        callback = new_packet.pop('on_voice_callback')

        if ret['err_msg'] == 'success.':
            result = ret['result'][0]  # 取出结果，返回给前端
            callback(result, True)
        else:
            callback('失败', False)

    def get_params_keys(self):
        return VoiceTranslate.keys
