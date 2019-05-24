from django import http
from django.core.cache import cache
from django.shortcuts import render

# Create your views here.
from django.views import View

from areas.models import Area
from meiduo_mall.utils.response_code import RETCODE


class SubAreasView(View):
    """子级地区"""

    def get(self, request, pk):
        """
        获取子级市或区
        :param request:
        :param pk:
        :return:
        """
        # 1.获取参数
        # 2.校验参数
        if not pk:
            return http.HttpResponseForbidden('缺少必要参数')
        sub_data = cache.get('sub_data'+pk)
        if not sub_data:
            # 3.遍历拼接数据
            sub_list = list()
            sub_objects = Area.objects.filter(parent=pk)
            for sub in sub_objects:
                sub_dict = {
                    "id":sub.id,
                    "name":sub.name
                }
                sub_list.append(sub_dict)
            # 4.再进行拼接
            sub_data = {
                "id":pk,
                "name":Area.objects.get(id=pk).name,
                "subs":sub_list
            }
            # 5.加入缓存
            try:
                cache.set('sub_data'+pk,sub_data,3600)
            except Exception as e:
                return http.JsonResponse({
                    "code":RETCODE.DBERR,
                    "errmsg":"加入缓存失败"
                })
        # 6.进行返回
        return http.JsonResponse({
            "code": RETCODE.OK,
            "errmsg": "OK",
            "sub_data":sub_data
        })


class ProvinceAreasView(View):
    """获取省级地区"""

    def get(self, request):
        """
        返回省级地区
        :param request:
        :return:
        """
        # 判断是否有缓存
        province_list = cache.get('province_list')
        if not province_list:
            # 1. 获取参数
            province_objects = Area.objects.filter(parent__isnull=True)
            # 2. 遍历拼接
            province_list = list()
            for province in province_objects:
                province_dict = {
                    "id": province.id,
                    "name": province.name
                }
                province_list.append(province_dict)
            # 3. 添加缓存
            try:
                cache.set('province_list', province_list, 3600)
            except Exception as e:
                return http.JsonResponse({
                    "code": RETCODE.DBERR,
                    "errmsg": "缓存保存错误",
                })
        return http.JsonResponse({
            "code": "0",
            "errmsg": "ok",
            "province_list": province_list
        })
