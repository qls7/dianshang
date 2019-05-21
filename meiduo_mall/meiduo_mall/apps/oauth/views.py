import json

import re
from QQLoginTool.QQtool import OAuthQQ
from django import http
from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection

from meiduo_mall.utils.response_code import RETCODE
from oauth.models import OAuthQQUser
from oauth.utils import general_access_token, check_access_token
import logging

from users.models import User

logger = logging.getLogger('django')


class QQUserView(View):
    """用户扫码登录的回调地址"""

    def get(self, request):
        """
        OAuth2.0认证
        获取code,获取openid,进行判断是否存在,
        存在返回登录成功,不存在加密openid返回前端
        :param request:
        :return:
        """
        # 获取code
        code = request.GET.get('code')
        # 创建oauth对象
        oauth = OAuthQQ(
            client_id=settings.QQ_CLIENT_ID,
            client_secret=settings.QQ_CLIENT_SECRET,
            redirect_uri=settings.QQ_REDIRECT_URI,
        )
        # 获取access_token
        access_token = oauth.get_access_token(code)
        # 获取openid
        openid = oauth.get_open_id(access_token)
        # 连接数据库
        redis_conn = get_redis_connection('verify_code')
        # 判断是否存在openid
        # openid是存在mysql里面的,OAuthQQUser表里面
        try:
            user = OAuthQQUser.objects.get(openid=openid)
        except Exception as e:
            # 不存在的情况,加密后,传给前端
            access_token = general_access_token(openid)
            return render(request, 'oauth_callback.html', {'access_token': access_token})
        else:
            # 存在,保持状态,设置cookie,返回首页
            login(request, user)
            response = redirect(reverse('contents:index'))
            response.set_cookie('username', user.username, max_age=3600 * 24 * 15)

    def post(self,request):
        """
        用户绑定qq
        :param request:
        :return:
        """
        # 接受参数 表单传参
        json_dict = json.loads(request.body.decode())
        mobile = json_dict.get('mobile')
        password = json_dict.get('password')
        sms_code_client = json_dict.get('sms_code')
        access_token = json_dict.get('access_token')

        # 校验参数
        if not all([mobile,password,sms_code_client,access_token]):
            return http.HttpResponseForbidden('缺少参数')
        if not re.match(r'^1[3-9]\d{9}$',mobile):
            return http.HttpResponseForbidden('手机格式不正确')
        if not re.match(r'^a-zA-Z0-9{8,20}$',password):
            return http.HttpResponseForbidden('密码格式不正确')
        # 链接redis查询验证码
        redis_conn = get_redis_connection('verify_code')
        try:
            sms_code_server = redis_conn.get('sms_%s' % mobile)
        except Exception as e:
            logger.error(e)
            return http.HttpResponseForbidden('验证码已经失效')
        else:
            if sms_code_client != sms_code_server:
                return http.HttpResponseForbidden('验证码错误')
        # 校验access_token
        openid = check_access_token(access_token)
        # 如果openid没有值,则验证失败
        if openid is None:
            return http.HttpResponseForbidden('openid错误')

        # 保存openid
        try:
            user = User.objects.create_user(username=mobile, password=password, mobile=mobile)
        except Exception as e:
            logger.error(e)
            return http.HttpResponseForbidden('OAuth2.0验证失败')
        try:
            user = OAuthQQUser.objects.create(openid=openid,user='users.User')
        except Exception as e:
            logger.error(e)
            return http.HttpResponseForbidden('OAuth2.0验证失败')
        # 保持状态 修改cookie
        login(request,user)
        response = redirect(reverse('contents:index'))
        response.set_cookie('username',user.username,3600*24*15)

        # 返回首页
        return response


class QQURLView(View):
    """请求QQ登录地址"""

    def get(self, request):
        """
        获取参数,返回QQ登录页面
        :param request:请求对象
        :return:JSON
        """
        next = request.GET.get('next')

        oauth = OAuthQQ(
            client_id=settings.QQ_CLIENT_ID,
            client_secret=settings.QQ_CLIENT_SECRET,
            redirect_uri=settings.QQ_REDIRECT_URI,
            state=next
        )
        login_url = oauth.get_qq_url()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok', 'login_url': login_url})