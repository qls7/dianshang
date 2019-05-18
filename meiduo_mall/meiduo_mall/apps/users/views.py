import re
from django import http
from django.contrib.auth import login
from django.db import DatabaseError
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views import View
from django_redis import get_redis_connection

from meiduo_mall.utils.response_code import RETCODE
from users.models import User


class MobileCountView(View):
    """判断用户手机号是否注册过"""

    def get(self, request, mobile):
        """
        接受手机号判断是否重复注册
        :param request: 请求对象
        :param mobile:手机号
        :return: JSON
        """
        count = User.objects.filter(mobile=mobile).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok', 'count': count})


class UsernameCountView(View):
    """判断用户名是否重复注册"""

    def get(self, request, username):
        """
        获取用户名统计数量并返回
        :param request:
        :param username:
        :return:
        """
        count = User.objects.filter(username=username).count()
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok', 'count': count})


class RegisterView(View):
    """
    用户注册
    """

    def get(self, request):
        """
        提供注册界面
        :param request: 提供在注册对象
        :return: 注册页面
        """
        return render(request, 'register.html')

    def post(self, request):
        """
        接收数据
        :param request:注册对象
        :return: 注册完成的页面
        """
        # 1.接受参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        sms_code_client = request.POST.get('sms_code')
        allow = request.POST.get('allow')
        # 2.校验参数
        if not all([username, password, password2, mobile, allow, sms_code_client]):
            return http.HttpResponseForbidden('缺少参数')

        if not re.match(r'^[a-zA-Z0-9_-]{5,20}$', username):
            return http.HttpResponseForbidden('用户名输入错误')

        if password != password2:
            return http.HttpResponseForbidden('两次的密码不一致')

        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseForbidden('密码格式不正确')

        if not re.match(r'^1[345789]\d{9}$', mobile):
            return http.HttpResponseForbidden('手机号格式不正确')

        # 获取短信验证码,进行校验
        redis_conn = get_redis_connection('verify_code')
        sms_code_server = redis_conn.get('sms_%s' % mobile).decode()
        # 判断数据库是否 存在短信验证码
        if sms_code_server is None:
            # 数据库不存在 验证码失效,返回注册页面
            # return http.HttpResponseForbidden('短信验证码已经失效')
            return render(request,'register.html',{'sms_code_errmsg':'无效的验证码'})

        if sms_code_client != sms_code_server:
            # return http.HttpResponseForbidden('短信验证码错误')
            return render(request,'register.html',{'sms_code_errmsg':'输入的短信验证码有误'})

        if allow != 'on':
            return http.HttpResponseForbidden('请勾选同意用户协议')

        # 3.保存数据到数据库
        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            return render(request, 'register.html', {'register_errmg': '注册失败'})
        # 实现状态保持,如果存入数据库成功的话
        login(request, user)

        # 4.进行返回 重定向首页
        return redirect(reverse('contents:index'))