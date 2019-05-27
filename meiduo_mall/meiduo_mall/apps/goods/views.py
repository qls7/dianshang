from django import http
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render

# Create your views here.
from django.views import View

from goods.models import GoodsCategory
from goods.utils import get_categories, get_breadcrumb


class ListView(View):
    """获取商品列表详情页"""

    def get(self, request, category_id, page_num):
        """
        展示商品列表详情页
        :param request:
        :return:
        """
        # 获取参数
        sort = request.GET.get('sort','default')
        # 校验参数
        # 路由里面已经进行过正则匹配了
        # if not all([category_id, page_num]):
        #     return http.HttpResponseForbidden('缺少必传参数')
        try:
            # 根据商品id获取商品列表并排序
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseNotFound('GoodCategory 不存在')

        # 获取商品类别
        categories = get_categories()
        # 根据商品类别id获取商品导航页
        breadcrumb = get_breadcrumb(category)
        # 根据sort的内容确定排序的方式
        if sort == 'price':
            sort_kind = 'price'
        elif sort == 'hot':
            sort_kind = '-sales'
        else:
            sort_kind = 'create_time'

        sku_s = category.sku_set.filter(is_launched=True).order_by(sort_kind)
        # 创建分页对象
        paginator = Paginator(sku_s, 5)
        # 根据页数返回页面的数据
        try:
            content = paginator.page(page_num)
        except EmptyPage:
            return http.HttpResponseNotFound('页面不存在')
        # 返回总页数
        page_nums = paginator.num_pages
        # 拼接数据进行返回
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sort': sort,
            'category': category,
            'page_skus': sku_s,
            'total_page': page_nums,
            'page_num': page_num
        }
        return render(request, 'list.html', context=context)
