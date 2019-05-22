import itsdangerous
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.

class User(AbstractUser):
    """自定义用户模型类"""

    # 在用户模型类中增加 mobile字段
    mobile = models.CharField(max_length=11, unique=True, verbose_name='手机号')
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')

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

    def check_verify_url(self, token):
        """
        验证邮箱链接
        :return:
        """
        serializer = itsdangerous.TimedJSONWebSignatureSerializer(secret_key=settings.SECRET_KEY, expires_in=3600 * 24)
        try:
            data = serializer.loads(token)
        except Exception:
            pass
