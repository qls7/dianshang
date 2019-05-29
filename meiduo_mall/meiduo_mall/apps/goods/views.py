from django import http
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render

# Create your views here.
from django.views import View

from goods.models import GoodsCategory, SKU
from goods.utils import get_categories, get_breadcrumb, get_goods_and_spec
from meiduo_mall.utils.response_code import RETCODE


class DetailView(View):
    """商品详情页"""

    def get(self, request, sku_id):
        """
        获取商品详情页
        :param request:
        :param sku_id:
        :return:
        """
        # 获取商品sku
        # try:
        #     sku = SKU.objects.get(id=sku_id)
        # except SKU.DoesNotExist:
        #     return render(request,'404.html')
        # 获取商品频道分类
        categories = get_categories()
        # 获取商品面包屑
        # category = sku.category
        # breadcrumb = get_breadcrumb(category)
        # 获取商品sku规格
        data = get_goods_and_spec(sku_id,request)
        # 获取热销排行
        # 直接将商品类返回给前端,前端会接收到商品类id主动请求
        # 获取商品详情售后服务

        # 组合参数
        context = {
            'categories':categories,
            'goods':data.get('goods'),
            'sku':data.get('sku'),
            'specs':data.get('goods_specs')
        }
        # 返回
        return render(request,'detail.html',context=context)


class HotGoodsView(View):
    """热销排行数据"""

    def get(self, request, category_id):
        """
        获取热销排行数据
        :param request:
        :param category_id:
        :return:
        """
        # 获取数据按销量进行排序并截取
        try:
            skus = SKU.objects.filter(category_id=category_id, is_launched=True).order_by('-sales')[:2]
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('category_id 不存在')
        # 遍历组装格式
        hot_skus = list()
        for sku in skus:
            hot_skus.append({
                'id': sku.id,
                'default_image_url': sku.default_image_url,
                'name': sku.name,
                'price': sku.price
            })
        # 返回
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'hot_skus': hot_skus})


class ListView(View):
    """获取商品列表详情页"""

    def get(self, request, category_id, page_num):
        """
        展示商品列表详情页
        :param request:
        :return:
        """
        # 获取参数
        sort = request.GET.get('sort', 'default')
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
