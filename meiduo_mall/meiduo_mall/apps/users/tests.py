from django import http
from django.test import TestCase

# Create your tests here.
from django.views import View


class test(View):
    """测试下get函数如果没有值会不会报错"""

    def get(self,request):
        """
        获取查询字符串的值
        :param request:
        :return:
        """
        a = request.GET.get('a')
        print(a)
        return http.HttpResponse(a)