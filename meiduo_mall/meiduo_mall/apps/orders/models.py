from django.db import models

# Create your models here.
from meiduo_mall.utils.models import BaseModel


class OrderInfo(BaseModel):
    """订单信息"""
    PAY_METHODS_ENUM = {
        'CASH': 1,
        'ALIPAY': 2
    }
    PAY_METHOD_CHOICES = (
        (1, '货到付款'),
        (2, '支付宝'),
    )
    ORDER_STATUS_ENUM = {
        'UNPAID': 1,
        'UNSEND': 2,
        'UNRECEIVED': 3,
        'UNCOMMENT': 4,
        'FINISHED': 5
    }
    ORDER_STATUS_CHOICES = (
        (1, '待支付'),
        (2, '待发货'),
        (3, '待收货'),
        (4, '待评价'),
        (5, '已完成'),
        (6, '已取消'),
    )
    order_id = models.CharField(primary_key=True, max_length=64, verbose_name='订单编号')
    user = models.ForeignKey('users.User', on_delete=models.PROTECT, verbose_name='下单用户')
    address = models.ForeignKey('users.Address', on_delete=models.PROTECT, verbose_name='收货地址id')
    total_count = models.IntegerField(verbose_name='商品总数', default=1)
    total_amount = models.DecimalField(verbose_name='订单总额', max_digits=10, decimal_places=2)
    freight = models.DecimalField(verbose_name='运费', max_digits=10, decimal_places=2)
    pay_method = models.SmallIntegerField(verbose_name='支付方式', choices=PAY_METHOD_CHOICES, default=1)
    status = models.SmallIntegerField(verbose_name='订单状态', choices=ORDER_STATUS_CHOICES, default=1)

    class Meta:
        """表格说明"""
        db_table = 'tb_order_info'
        verbose_name = '订单基本信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.order_id


class OrderGoods(BaseModel):
    """订单商品"""
    SCORE_CHOICES = (
        (0, '0分'),
        (1, '20分'),
        (2, '40分'),
        (3, '60分'),
        (4, '80分'),
        (5, '100分'),
    )
    order = models.ForeignKey(OrderInfo, on_delete=models.CASCADE, related_name='skus', verbose_name='订单编号')
    sku = models.ForeignKey('goods.SKU', on_delete=models.PROTECT, verbose_name='订单商品')
    count = models.IntegerField(verbose_name='商品数量', default=1)
    price = models.DecimalField(verbose_name='下单时单价', max_digits=10, decimal_places=2)
    comment = models.TextField(verbose_name='商品评论', default='')
    score = models.SmallIntegerField(verbose_name='商品评分', default=5, choices=SCORE_CHOICES)
    is_anonymous = models.BooleanField(verbose_name='是否匿名评价', default=False)
    is_commented = models.BooleanField(verbose_name='是否评价完成', default=False)

    class Meta:
        db_table = 'tb_order_goods'
        verbose_name = '订单商品'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.sku.name
