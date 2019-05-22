import os

from celery import Celery

# 使用 django 配置文件进行设置
os.environ.setdefault('DJANGO_SETTINGS_MODULE','meiduo_mall.settings.dev')
# 创建 celery 实例
celery_app = Celery('meido')
# 加载 celery 配置
celery_app.config_from_object('celery_tasks.config')
# 自动注册 celery 任务
celery_app.autodiscover_tasks(['celery_tasks.sms','celery_tasks.email'])
# celery_app.autodiscover_tasks(['celery_tasks.email'])


