import itsdangerous
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
import logging

from meiduo_mall.utils.models import BaseModel

logger = logging.getLogger('django')
# Create your models here.
from itsdangerous import BadData


class Address(BaseModel):
    """用户地址"""
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='addresses', verbose_name='用户名')
    province = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='provinces', verbose_name='省')
    city = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='cities', verbose_name='市')
    district = models.ForeignKey('areas.Area', on_delete=models.PROTECT, related_name='districts', verbose_name='区')
    title = models.CharField(max_length=20, verbose_name='标题')
    receiver = models.CharField(max_length=20, verbose_name='收货人')
    mobile = models.CharField(max_length=11,verbose_name='电话')
    place = models.CharField(max_length=50, verbose_name='收货地址')
    tel = models.CharField(max_length=20, verbose_name='固定电话', null=True, blank=True, default='')
    email = models.CharField(max_length=30, verbose_name='邮箱', null=True, blank=True, default='')
    is_deleted = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        db_table = 'tb_address'
        verbose_name = '用户地址'
        verbose_name_plural = verbose_name
        ordering = ['-update_time']


class User(AbstractUser):
    """自定义用户模型类"""

    # 在用户模型类中增加 mobile字段
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')
    # 默认地址外键
    default_address = models.ForeignKey(Address, on_delete=models.SET_NULL, related_name='users', verbose_name='默认地址',
                                        null=True, blank=True)

    # 对当前表进行相关设置:
    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

    # 在 str 魔法方法中,返回用户名称

    def __str__(self):
        return self.username

    def general_verify_url(self):
        """
        生成验证邮箱链接
        :return:
        """
        data = {
            'id': self.id,
            'email': self.email
        }
        serializer = itsdangerous.TimedJSONWebSignatureSerializer(secret_key=settings.SECRET_KEY, expires_in=3600 * 24)
        token = serializer.dumps(data).decode()
        verify_url = settings.EMAIL_VERIFY_URL + '?token=' + token
        return verify_url

    @staticmethod
    def check_verify_url(token):
        """
        验证邮箱链接
        :return:
        """
        serializer = itsdangerous.TimedJSONWebSignatureSerializer(secret_key=settings.SECRET_KEY, expires_in=3600 * 24)
        try:
            data = serializer.loads(token)
        except BadData:
            return None
        else:
            id = data.get('id')
            email = data.get('email')
        try:
            user = User.objects.get(id=id, email=email)
        except User.DoesNotExist:
            return None
        else:
            return user
