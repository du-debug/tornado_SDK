"""
制造签名的中间键
"""
import hashlib

class SignMixin(object):
    """签名"""
    def send_order_sign(self, params):
        print('**send_order_sign:params:{}**'.format(params))
        keys = sorted(filter(lambda x: x != "sign", params.keys()))
        sign_str = ['%s=%s' % (key, params.get(key, '')) for key in params.keys() if params.get(key) != '']
        key_str = ''  # TODO 加密的钥匙在apps表里面进行配置，后续进行处理
        sign = hashlib.md5(sign_str + key_str).hexdigest()
        return sign

    def check_sign(self, packet):
        sign_str = '&'.join(['{}={}'.format(key, str(packet[key])) for key in sorted(packet) if key != 'sign'])
        sign_str += "app_key"  # TODO app_key 存于数据库中
        sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest()
        return sign


if __name__ == "__main__":
    test = SignMixin()
    params = dict(
        a='1',
        b='2',
        c='3'
    )
    print(test.check_sign(params))