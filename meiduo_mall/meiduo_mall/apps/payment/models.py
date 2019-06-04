from django.db import models

# Create your models here.
from meiduo_mall.utils.models import BaseModel
from orders.models import OrderInfo


class Payment(BaseModel):
    """支付信息"""
    order = models.ForeignKey(OrderInfo, on_delete=models.PROTECT, verbose_name='订单编号')
    trade_id = models.CharField(verbose_name='支付编号', max_length=100, unique=True, null=True, blank=True)

    class Meta:
        db_table = 'tb_payment'
        verbose_name = '支付信息'
        verbose_name_plural = verbose_name