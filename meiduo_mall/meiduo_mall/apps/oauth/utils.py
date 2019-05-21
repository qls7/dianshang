import itsdangerous
from django.conf import settings


def general_access_token(openid):
    """
    生成access_token
    :param openid:
    :return:
    """
    # 先创建itsdangerous里面timeweb的对象
    serializer = itsdangerous.TimedJSONWebSignatureSerializer(settings.SECRET_KEY, expires_in=300)
    # 进行加密
    data = {
        'openid': openid
    }
    # 加密完是二进制,要先进行解码
    access_token = serializer.dumps(data).decode()

    return access_token


def check_access_token(access_token):
    """
    对access_token进行解密生成openid
    :param access_token:
    :return:
    """
    serializer = itsdangerous.TimedJSONWebSignatureSerializer(settings.SECRET, expires_in=300)
    openid = serializer.loads(access_token)

    return openid.get('openid')