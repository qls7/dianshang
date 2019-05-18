import random

from django import http
from django.shortcuts import render
import logging

from meiduo_mall.libs.yuntongxun.ccp_sms import CCP

logger = logging.getLogger('django')
# Create your views here.
from django.views import View
from django_redis import get_redis_connection

from meiduo_mall.libs.captcha.captcha import captcha
from meiduo_mall.utils.response_code import RETCODE
from verifications import const


class SMSCodeView(View):
    """短信验证码"""

    def get(self, request, mobile):
        """
        接受手机号,图片验证码,进行校验,返回短信验证码
        :param request:请求对象
        :param mobile: 手机号
        :return: JSON
        """
        # 进行时间验证,如果在一分钟内请求了多次直接返回
        redis_conn = get_redis_connection('verify_code')  # 注意不要打错了数据库的名字
        if redis_conn.get('send_flag_%s' % mobile):
            return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '发送短信过于频繁'})

        # 1.获取图片验证码
        image_code_client = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')
        # 2.进行校验
        # 2.1 全局校验
        if not all([image_code_client, uuid]):
            return http.JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '缺少参数'})
        # 3.提取验证码
        image_code_server = redis_conn.get('img_%s' % uuid)
        # 4.如果验证码不存在或过期
        if image_code_server is None:
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '验证码失效'})
        # 5.删除图形验证码,避免恶意测试图形验证码
        try:
            redis_conn.delete('img_%s' % uuid)
        except Exception as e:
            logger.error(e)
        # 6.对比验证码,注意转成字符串,变小写
        if image_code_client.lower() != image_code_server.decode().lower():
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '输入图形验证码有误'})

        # 7.生成短信验证码,保存并发送
        sms_code = '%06d' % random.randint(0,999999) # randint需要两个参数注意不要用一个参数
        # 打印下验证码
        print('-'*50)
        logger.info(sms_code)
        # 8.保存

        # redis_conn.setex('sms_%s'%mobile,const.SMS_CODE_EXPIRES,sms_code)
        # redis_conn.setex('sms_flag_%s'%mobile,const.SMS_CODE_EXPIRES,1)

        # pipline 管道操作Redis数据库,可以一次性发送多条命令并在执行完后一次性将结果返回

        pl = redis_conn.pipeline()
        pl.setex('sms_%s'%mobile,const.SMS_CODE_EXPIRES,sms_code)
        pl.setex('sms_flag_%s'%mobile,const.SMS_CODE_EXPIRES,1)
        pl.execute()

        # 9.发送
        # CCP().send_template_sms(mobile, [sms_code,5], const.SEND_SMS_TEMPLATE_ID)

        # 异步方案 RabbitMQ和Celery
        from celery_tasks.sms.tasks import ccp_send_sms_code
        ccp_send_sms_code.delay(mobile,sms_code)
        # 10.响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '发送短信成功'})


class ImageCodeView(View):
    """生成图片验证码"""

    def get(self, request, uuid):
        """

        :param request: 请求对象
        :param uuid: 唯一标示图形验证码所属于的用户
        :return: image/jpg
        """
        # 1.获取uuid
        # 2.根据uuid生成图片验证码(添加captcha包,安装Pillow(python处理程序要用的包))
        text, image = captcha.generate_captcha()
        # 3.保存验证码到redis
        redis_conn = get_redis_connection('verify_code')
        redis_conn.setex('img_%s' % uuid, const.IMAGE_CODE_REDIS_EXPIRES, text)
        # 4.返回图片
        return http.HttpResponse(image, content_type='image/jpg')
