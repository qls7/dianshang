from decimal import Decimal
from django.shortcuts import render

# Create your views here.
from django.views import View
from django_redis import get_redis_connection

from goods.models import SKU
from meiduo_mall.utils.response_code import RETCODE
from meiduo_mall.utils.views import LoginRequiredMixin
from users.models import Address


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
