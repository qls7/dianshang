from celery_tasks.main import celery_app
from celery_tasks.yuntongxun.ccp_sms import CCP
import logging

logger = logging.getLogger('django')


@celery_app.task(bind=True,name='ccp_send_sms_code', retry_backoff=3)
def ccp_send_sms_code(self, mobile, sms_code):
    """
    发送短信任务
    :param self:保证task对象会作为第一个参数自动传入
    :param mobile: 手机号
    :param sms_code: 短信验证码
    :return: 成功0 或失败-1
    """
    try:
        # 调用ccp()发送短信,并传递相关参数:
        result = CCP().send_template_sms(mobile, [sms_code, 5], 1)
    except Exception as e:
        logger.error(e)

        raise self.retry(exc=e, max_retries=3)

    if result != 0:
        raise self.retry(exc=Exception('发送短信失败'), max_retries=3)
    return result
