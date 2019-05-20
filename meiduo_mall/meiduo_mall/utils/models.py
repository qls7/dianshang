from django.db import models


class BaseModel(models.Model):
    """为模型类添加默认字段(增加时间和修改时间)"""
    create_time = models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True,verbose_name='更新时间')

    class Meta:
        # 指明为抽象模型类,即在迁移的时候不会生成BaseModel表
        abstract = True
