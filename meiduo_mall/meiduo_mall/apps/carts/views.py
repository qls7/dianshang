import base64
import json

import pickle

from django import http
from django.shortcuts import render

# Create your views here.
from django.views import View
from django_redis import get_redis_connection

from goods.models import SKU
from meiduo_mall.utils.response_code import RETCODE


class CartsSelectAllView(View):
    """全选购物车"""

    def put(self, request):
        """
        全选购物车
        :param request:
        :return:
        """
        # 1.获取参数
        json_dict = json.loads(request.body.decode())
        selected = json_dict.get('selected')
        # 2.校验参数
        if not selected:
            
        # 3.判断用户是否登录
        # 4.如果登录成功
        # 5.连接redis 获取hash的数据
        # 6.判断selected的值
        # 7.如果是True把所有的key值都加入到set中
        # 8.如果都是False把所有的key都删除
        # 9.返回
        # 10.如果登录不成功
        # 11.获取cookie的值,解密
        # 12.把selected的值重新赋值给字典中的selected
        # 13.加密
        # 14.返回

class CartsView(View):
    """购物车管理"""

    def delete(self, request):
        """
        删除购物车里面的数据
        :param request:
        :return:
        """
        # 获取参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        # 校验参数
        try:
            SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('sku_id 不存在')
        # 判断用户是否登录
        if request.user.is_authenticated:
            # 如果登录
            # 链接redis 对hash和set里的数据进行删除
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            pl.hdel('carts_%s' % request.user.id, sku_id)
            pl.srem('selected_%s' % request.user.id, sku_id)

            pl.execute()
            # 返回
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok'})

        else:
            # 如果没有登录
            cookie_cart = request.COOKIES.get('carts')

            if cookie_cart:
                # 获取cookie中的值
                # 解密
                cart_dict = pickle.loads(base64.b64decode(cookie_cart.encode()))
            else:
                cart_dict = {}

            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok'})

            # 删除对应的键的值
            if sku_id in cart_dict:
                del cart_dict[sku_id]
                # 重新加密cookie
                carts = base64.b64encode(pickle.dumps(cart_dict)).decode()
                # 设置cookie
                response.set_cookie('carts', carts)
            # 返回
            return response

    def put(self, request):
        """修改购物车"""
        # 接收参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)
        # 校验参数
        if not all([sku_id, count]):
            return http.HttpResponseForbidden('缺少必传参数')
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('sku_id错误')
        try:
            count = int(count)
        except Exception:
            return http.HttpResponseForbidden('count参数类型错误')
        if selected:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('selected参数错误')
        # 判断用户是否登录
        if request.user.is_authenticated:
            # 如果登录了
            # 链接redis数据库
            redis_conn = get_redis_connection('carts')
            # 直接进行修改,直接覆盖,状态分开修改
            pl = redis_conn.pipeline()
            pl.hset('carts_%s' % request.user.id, sku_id, count)
            if selected:
                pl.sadd('selected_%s' % request.user.id, sku_id)
            else:
                pl.srem('selected_%s' % request.user.id, sku_id)
            # 不要忘记最后进行执行提交
            pl.execute()
            # 创建响应对象进行返回
            cart_sku = {
                'id': sku.id,
                'name': sku.name,
                'count': count,
                'selected': selected,
                'default_image_url': sku.default_image_url,
                'price': sku.price,
                'amount': sku.price * count,

            }
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok', 'cart_sku': cart_sku})
        else:
            # 如果没有登录
            # 从cookie中取值
            carts = request.COOKIES.get('carts')
            # 判断cookie是否存在
            if carts:
                # 存在就直接解码生成字典
                carts_dict = pickle.loads(base64.b64decode(carts))
            else:
                # 不存在就生成字典
                carts_dict = {}
            # 直接进行修改
            carts_dict[sku_id] = {
                'count': count,
                'selected': selected
            }

            # 拼接数据格式
            cart_sku = {
                'id': sku.id,
                'name': sku.name,
                'count': count,
                'selected': selected,
                'default_image_url': sku.default_image_url,
                'price': sku.price,
                'amount': sku.price * count,

            }
            # 设置cookie
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok', 'cart_sku': cart_sku})

            carts = base64.b64encode(pickle.dumps(carts_dict)).decode()
            response.set_cookie('carts', carts)
            # 返回
            return response

    def get(self, request):
        """
        展示购物车数据
        :param request:
        :return:
        """
        # 判断用户是否登录
        user_id = request.user.id
        if request.user.is_authenticated:
            # 如果已登录
            # 链接redis数据库
            redis_conn = get_redis_connection('carts')
            # 取出数据,转成cookie格式
            sku_dict = redis_conn.hgetall('carts_%s' % user_id)
            selected_list = redis_conn.smembers('selected_%s' % user_id)
            carts_dict = {}
            for sku_id, count in sku_dict.items():
                carts_dict[int(sku_id)] = {
                    'count': int(count),
                    'selected': sku_id in selected_list,
                }
        else:
            # 如果没有登录
            # 取出cookie的值
            carts = request.COOKIES.get('carts')
            # 判断carts是否存在
            if carts:
                # 如果存在
                # 解码生成字典
                carts_dict = pickle.loads(base64.b64decode(carts))
            else:
                # 如果不存在新建一个空字典
                carts_dict = {}

        # 对字典进行遍历取出key和value进行拼接数据返回
        cart_skus = list()
        skus = SKU.objects.filter(id__in=carts_dict.keys())
        for sku in skus:
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'count': carts_dict.get(sku.id).get('count'),
                'selected': str(carts_dict.get(sku.id).get('selected')),
                'default_image_url': sku.default_image_url,
                'price': str(sku.price),
                'amount': str(sku.price * carts_dict.get(sku.id).get('count'))
            })

        context = {

            'cart_skus': cart_skus
        }
        return render(request, 'cart.html', context=context)

    def post(self, request):
        """
        添加购物车
        :param request:
        :return:
        """
        # 获取参数
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        selected = json_dict.get('selected', True)
        # 校验参数
        if not all([sku_id, count]):
            return http.HttpResponseForbidden('缺少必传参数')
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('sku_id错误')
        try:
            count = int(count)
        except Exception:
            return http.HttpResponseForbidden('count参数类型错误')
        if selected:
            if not isinstance(selected, bool):
                return http.HttpResponseForbidden('selected参数错误')
        # 判断是否登录
        if request.user.is_authenticated():
            # 如果登录
            # 链接redis,直接进行存储
            redis_conn = get_redis_connection('carts')
            pl = redis_conn.pipeline()
            # 分两部分存储
            # hash user_%id :{ sku.id:count }
            # set selected_%user.id(sku.id,sku.id...)
            pl.hincrby('carts_%s' % request.user.id, sku_id, count)
            if selected:
                # 如果是真的情况下在进行添加
                pl.sadd('selected_%s' % request.user.id, sku_id)
            pl.execute()

            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok'})

        else:
            # 如果没登录
            # 获取cookie
            carts = request.COOKIES.get('carts')
            # 判断是否有cookie
            if carts:
                # 如果有进行解码生成字典
                cart_dict = pickle.loads(base64.b64decode(carts.encode()))

            else:
                # 如果没有新建一个字典
                cart_dict = dict()
            # 对字典存在这个id值,直接进行添加
            if sku_id in cart_dict:
                count += cart_dict[sku_id]['count']

            cart_dict[sku_id] = {
                'count': count,
                'selected': selected,
            }

            # 对字典进行加密
            carts_data = base64.b64encode(pickle.dumps(cart_dict)).decode()
            # 拼接
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok'})
            response.set_cookie('carts', carts_data)
            # 返回
            return response
