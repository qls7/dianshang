from django.shortcuts import render

# Create your views here.
from django.views import View

from contents.models import ContentCategory
from goods.utils import get_categories


class IndexView(View):
    """首页广告"""

    def get(self,request):
        """
        提供首页广告界面
        :param request:
        :return:
        """
        # 获取商品频道及类别
        categories = get_categories()
        # 获取所有首页广告类别
        contents = ContentCategory.objects.all()
        content = dict()
        # 遍历所有的广告获取所有类别对应的广告的信息(定义一个字典,存放广告类别的key对应的value是此条广告类别所有的广告的对象)
        for con in contents:
            content[con.key] = con.content_set.filter(status=True).order_by('sequence')
        #
        context = {
            'categories':categories,
            'contents':content
        }

        return render(request,'index.html',context=context)