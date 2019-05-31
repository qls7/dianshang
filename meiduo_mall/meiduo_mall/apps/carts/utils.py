import base64
import pickle

from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request, response, user):
    """
    合并cookie中的数据到redis
    :param request:
    :param response:
    :param user:
    :return:
    """
    # 1.获取cookie中的数据
    cookie_cart = request.COOKIES.get('carts')
    if not cookie_cart:
        return response
    # 2.解密进行拼接
    cart_dict = pickle.loads(base64.b64decode(cookie_cart))
    new_cart_dict = {}
    new_add = []
    new_rem = []
    for spu_id, count in cart_dict.items():
        new_cart_dict[spu_id] = count['count']
        if cart_dict[spu_id]['selected']:
            # 3.如果是选中状态保存增加列表
            new_add.append(spu_id)
        else:
            # 4.如果是没选中状态保存删除列表
            new_rem.append(spu_id)
    # 5.连接redis数据库
    redis_conn = get_redis_connection('carts')
    pl = redis_conn.pipeline()
    # 6.进行合并操作,有的话直接覆盖redis中的数据
    pl.hmset('carts_%s' % user.id, new_cart_dict)
    if new_add:
        pl.sadd('selected_%s' % user.id, *new_add)
    if new_rem:
        pl.srem('selected_%s' % user.id, *new_rem)
    pl.execute()
    # 7.删除cookie中的值
    response.delete_cookie('carts')
    # 8.返回response
    return response
