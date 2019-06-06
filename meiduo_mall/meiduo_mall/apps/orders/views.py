import json
from decimal import Decimal

from django import http
from django.core.paginator import Paginator, EmptyPage
from django.db import transaction
from django.shortcuts import render

# Create your views here.
from django.utils import timezone
from django.views import View
from django_redis import get_redis_connection

from goods.models import SKU
from meiduo_mall.utils.response_code import RETCODE
from meiduo_mall.utils.views import LoginRequiredMixin, LoginRequiredJSONMixin
from orders.models import OrderInfo, OrderGoods
from users.models import Address
import logging

logger = logging.getLogger('django')


class OrderCommentView(LoginRequiredMixin, View):
    """订单商品评价"""

    def get(self, request):
        """
        订单商品评价
        :param request:
        :return:
        """
        # 1.获取参数
        order_id = request.GET.get('order_id')
        # 2.校验参数
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=request.user)
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('订单不存在')
        # 3.根据订单编号获取所有的商品行
        try:
            uncomment_goods = order.skus.filter(is_commented=False, order_id=order_id)
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('没有未评价的商品')
        # 构造带评价商品数据
        uncomment_goods_list = []
        # 4.遍历每个商品行, 拿到每行具体的商品
        for goods in uncomment_goods:
            sku = goods.sku
            uncomment_goods_list.append({
                'order_id': order_id,
                'sku_id': sku.id,
                'name': sku.name,
                'price': str(goods.price),
                'default_image_url': sku.default_image_url,
                'comment': goods.comment,
                'score': goods.score,
                'is_anonymous': str(goods.is_anonymous),
            })
        # 5.渲染模板
        context = {
            'code': RETCODE.OK,
            'errmsg': 'ok',
            'uncomment_goods_list': uncomment_goods_list
        }
        # 6.返回
        return render(request, 'goods_judge.html', context)

    def post(self, request):
        """获取参数修改评论页面的内容"""
        # 1.获取参数
        json_dict = json.loads(request.body.decode())
        order_id = json_dict.get('order_id')
        sku_id = json_dict.get('sku_id')
        score = json_dict.get('score')
        comment = json_dict.get('comment')
        is_anonymous = json_dict.get('is_anonymous')
        # 2.校验参数
        try:
            # 先在订单信息表中判断该订单是否是该用户的订单
            order_info = OrderInfo.objects.get(order_id=order_id, user=request.user)
        except OrderInfo.DoesNotExist:
            return http.HttpResponseForbidden('order_id 参数错误')
        try:
            # 再在sku表中判断该商品是否存在
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('sku_id 参数错误')
        if is_anonymous:
            if not isinstance(is_anonymous, bool):
                return http.HttpResponseForbidden('is_anonymous 参数错误')
        # 3.写入数据库
        try:
            OrderGoods.objects.filter(order_id=order_id, sku_id=sku_id).update(
                comment=comment,
                score=score,
                is_anonymous=is_anonymous,
                is_commented=True
            )
        except Exception:
            return http.HttpResponseForbidden('评论失败')
        sku.comments += 1
        sku.save()

        sku.goods.comments += 1
        sku.goods.save()

        # 修改订单状态
        if OrderGoods.objects.filter(order_id=order_id, is_commented=False).count() == 0:
            order_info.status = OrderInfo.ORDER_STATUS_ENUM['FINISHED']
            order_info.save()
        # 4.进行返回
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok'})


class UserOrderInfoView(LoginRequiredMixin, View):
    """我的订单"""

    def get(self, request, page_num):
        """
        获取用户订单的所有商品
        :param request:
        :param page_num:
        :return:
        """
        # 1.获取user
        user = request.user
        # 2.根据user获取所有订单信息
        orders = user.orderinfo_set.all().order_by('-create_time')
        # 3.遍历所有订单,根据订单获取每个订单的所有sku_ids
        for order in orders:
            # 绑定订单支付状态
            order.status_name = OrderInfo.ORDER_STATUS_CHOICES[order.status - 1][1]
            # 绑定订单支付方式
            order.pay_method_name = OrderInfo.PAY_METHOD_CHOICES[order.pay_method - 1][1]
            # 把每行的订单列表记录
            order.sku_list = []
            # 根据订单的商品信息获取对应的订单sku
            # 根据需求返回每页的具体数据
            order_goods = order.skus.all()
            for order_good in order_goods:
                sku = order_good.sku
                sku.count = order_good.count
                sku.amount = sku.price * sku.count
                order.sku_list.append(sku)
        # 6.增加分页功能
        page_num = int(page_num)
        try:
            # 导入Paginator,创建分页对象(指定分页对象集和每页显示的个数)
            paginator = Paginator(orders, 2)
            # 根据页码返回每页的内容
            page_orders = paginator.page(page_num)
            # 返回总页数,paginator.num_pages
            total_page = paginator.num_pages
        except EmptyPage:
            # 返回页面不存在的异常
            return http.HttpResponseForbidden('订单不存在')
        # 7.拼接返回
        context = {
            'page_orders': page_orders,
            'total_page': total_page,
            'page_num': page_num
        }

        return render(request, 'user_center_order.html', context)


class OrderSuccessView(LoginRequiredMixin, View):
    """展示提交订单成功页面"""

    def get(self, request):
        """返回订单提交成功页面"""
        # 1.获取参数
        order_id = request.GET.get('order_id')
        payment_amount = request.GET.get('payment_amount')
        pay_method = request.GET.get('pay_method')
        # 2.拼接返回
        context = {
            'code': RETCODE.OK,
            'errmsg': 'ok',
            'order_id': order_id,
            'payment_amount': payment_amount,
            'pay_method': pay_method,
        }
        return render(request, 'order_success.html', context)


class OrderCommitView(LoginRequiredJSONMixin, View):
    """订单提交"""

    def post(self, request):
        """
        返回提交订单页面
        :param request:
        :return:
        """
        # 1.接受参数(地址id,支付方式)
        json_dict = json.loads(request.body.decode())
        address_id = json_dict.get('address_id')
        pay_method = json_dict.get('pay_method')
        # 2.校验参数
        if not all([address_id, pay_method]):
            return http.HttpResponseForbidden('缺少必传参数')
        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return http.HttpResponseForbidden('address_id 参数错误')
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return http.HttpResponseForbidden('pay_method 参数错误')
        # 3.获取当前用户
        user = request.user
        # 4.存储订单信息表(生成订单编号,)
        time = timezone.localtime()
        time_str = time.strftime('%Y%m%d%H%M%S')
        order_id = time_str + '%09d' % user.id
        # pay_method = int(pay_method)
        # with下的代码都放在一个事物里面进行
        with transaction.atomic():
            save_point = transaction.savepoint()
            try:
                # 用户订单表修改
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=0,
                    total_amount=Decimal('0.00'),
                    freight=Decimal('10.00'),
                    pay_method=pay_method,
                    # 用模型类OrderInfo里面的字典来判断具体对应的值,避免在程序中出现数字
                    status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']
                    if pay_method == OrderInfo.PAY_METHODS_ENUM['ALIPAY']
                    else OrderInfo.ORDER_STATUS_ENUM['UNSEND']
                )

                # 保存订单商品信息
                # 5.连接redis
                redis_conn = get_redis_connection('carts')
                # 6.获取所有的selected的sku_id
                item_dict = redis_conn.hgetall('carts_%s' % user.id)
                selected_list = redis_conn.smembers('selected_%s' % user.id)
                # 7.组建一个sku_id:count字典,count就是用户要买的数量
                cart = {}
                for sku_id in selected_list:
                    cart[int(sku_id)] = int(item_dict[sku_id])
                # 8.获取所有的sku_ids
                sku_ids = cart.keys()
                # 使用乐观锁进行处理并发的状况
                # 9.遍历所有的sku_ids
                for sku_id in sku_ids:
                    while True:
                        # 10.获取一个sku,添加属性count
                        sku = SKU.objects.get(id=sku_id)
                        sku.count = cart[sku.id]
                        # 11.获取仓库库存,进行比较,如果没有库存,直接进行返回
                        origin_stock = sku.stock
                        origin_sales = sku.sales
                        if sku.count > origin_stock:
                            # 如果出现不一致进行回滚
                            transaction.savepoint_rollback(save_point)
                            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '库存不足'})
                        # 12.如果有库存进行修改sku库存,销量
                        # SKU表修改
                        # sku.stock -= sku.count
                        # sku.sales += sku.count
                        # sku.save()
                        # 使用乐观锁,一步进行更新操作
                        new_stock = origin_stock - sku.count
                        new_sales = origin_sales + sku.count
                        ret = SKU.objects.filter(stock=origin_stock, id=sku.id).update(
                            stock=new_stock,
                            sales=new_sales
                        )
                        if ret == 0:
                            continue
                        # 往order goods表中添加数据
                        # 订单商品表修改
                        OrderGoods.objects.create(
                            order=order,
                            sku=sku,
                            count=sku.count,
                            price=sku.price,
                        )
                        # 13.修改spu销量,修改订单信息表OrderInfo里面的订单总数,订单总金额
                        goods = sku.goods
                        goods.sales += sku.count
                        goods.save()

                        order.total_count += sku.count
                        order.total_amount += Decimal(sku.count * sku.price)
                        break
                # 添加邮费和保存订单信息
                order.total_amount += order.freight
                order.save()

                # 14.修改完进行删除hash和set
                redis_conn.hdel('carts_%s' % user.id, *selected_list)
                redis_conn.srem('selected_%s' % user.id, *selected_list)
                redis_conn.save()
            except Exception as e:
                logger.error(e)
                # 事物回滚
                transaction.savepoint_rollback(save_point)
                return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '下单失败'})
            # 如果没有出错,进行提交事物
            transaction.savepoint_commit(save_point)
        # 15.拼接数据进行返回(code,errmsg,order_id)
        return http.JsonResponse({
            'code': RETCODE.OK,
            'errmsg': 'OK',
            'order_id': order_id
        })


class OrderSettlementView(LoginRequiredMixin, View):
    """结算订单"""

    def get(self, request):
        """展示结算订单页面"""
        # 1.获取当前用户
        user = request.user
        # 2.根据用户id获取地址
        try:
            addresses = Address.objects.filter(user=user)
        except Address.DoesNotExist:
            addresses = None
        # 3.连接redis数据库
        redis_conn = get_redis_connection('carts')
        # 4.获取hash和set的数据hash:user_id:{sku_id:count,sku_id1:count1} set:[sku_id1,sku_id2]
        dict = redis_conn.hgetall('carts_%s' % user.id)
        selected_list = redis_conn.smembers('selected_%s' % user.id)
        # 5.根据set表中的sku_id获取hash表中的数量
        cart_dict = {}
        for sku_id in selected_list:
            cart_dict[int(sku_id)] = int(dict[sku_id])
            # 6.获取所有的sku_id
        sku_ids = cart_dict.keys()
        # 7.获取所有的商品
        skus = SKU.objects.filter(id__in=sku_ids)
        # 8.遍历所有的商品
        total_count = 0
        total_amount = Decimal('0.00')
        for sku in skus:
            # 9.拼接商品列表
            # 10.增加count和amount属性
            sku.count = cart_dict[sku.id]
            sku.amount = sku.count * sku.price
            # 11.累计计算商品数量和,商品总价
            total_count += sku.count
            total_amount += sku.amount
        # 12.增加邮费属性
        freight = Decimal('10.00')
        # 13.拼接返回
        context = {
            'addresses': addresses,
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
            'freight': freight,
            'payment_amount': total_amount + freight
        }
        return render(request, 'place_order.html', context)
