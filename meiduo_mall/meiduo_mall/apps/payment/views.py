import os

from alipay import AliPay
from django import http
from django.conf import settings
from django.shortcuts import render

# Create your views here.
from django.views import View

from meiduo_mall.utils.response_code import RETCODE
from meiduo_mall.utils.views import LoginRequiredJSONMixin, LoginRequiredMixin
from orders.models import OrderInfo
from payment.models import Payment


class PaymentStatusView(LoginRequiredMixin, View):
    """保存订单支付结果"""

    def get(self, request):
        """
        接收支付宝返回的页面
        :param request:
        :return:
        """
        # 1.接收参数
        data = request.GET.dict()
        signature = data.pop('sign')
        # 2.调用alipay库进行校验参数
        # 创建支付宝支付对象
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "keys/alipay_public_key.pem"),
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG
        )
        success = alipay.verify(data, signature)
        if success:
            # 3.如果成功
            # 获取订单编号
            order_id = data.get('out_trade_no')
            # 获取支付宝流水号
            trade_id = data.get('trade_no')
            # 4.保存到数据库
            Payment.objects.create(order_id=order_id, trade_id=trade_id)
            # 5.更改订单状态
            OrderInfo.objects.filter(order_id=order_id,
                                  status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']).update(
                                  status=OrderInfo.ORDER_STATUS_ENUM['UNCOMMENT'])
            context = {
                'trade_id':trade_id
            }
            return render(request, 'pay_success.html', context)
        # 6.如果不成功
        else:
            # 7.返回订单失败
            return http.HttpResponseForbidden('非法请求')


class PaymentView(LoginRequiredJSONMixin, View):
    """订单支付功能"""

    def get(self, request, order_id):
        """
        返回需要支付的支付宝链接
        :param request:
        :param order_id:
        :return:
        """
        # 1.校验参数
        try:
            order = OrderInfo.objects.get(order_id=order_id)
        except OrderInfo.DoesNotExist:
            # 2.判断订单编号是否合法
            return http.HttpResponseForbidden('order_id 参数错误')
        # 3.创建alipay对象
        # 创建支付宝支付对象
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                              "keys/app_private_key.pem"),
            alipay_public_key_path=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                "keys/alipay_public_key.pem"),
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG
        )
        # 4.根据对象调用方法生成查询字符串
        # 生成登录支付宝连接
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount),
            subject="美多商城%s" % order_id,
            return_url=settings.ALIPAY_RETURN_URL,
        )
        # 5.拼接地址进行返回
        # 真实环境电脑网站支付网关：https://openapi.alipay.com/gateway.do? + order_string
        # 沙箱环境电脑网站支付网关：https://openapi.alipaydev.com/gateway.do? + order_string
        alipay_url = settings.ALIPAY_URL + '?' + order_string
        return http.JsonResponse(
            {
                'code': RETCODE.OK,
                'errmsg': 'ok',
                'alipay_url': alipay_url
            }
        )
