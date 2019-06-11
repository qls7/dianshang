import datetime
from django import http
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render

# Create your views here.
from django.utils import timezone
from django.views import View
import logging

from orders.models import OrderGoods

logger = logging.getLogger('django')
from goods.models import GoodsCategory, SKU, GoodsVisitCount
from goods.utils import get_categories, get_breadcrumb, get_goods_and_spec
from meiduo_mall.utils.response_code import RETCODE


class GoodsCommentView(View):
    """订单商品评价信息"""

    def get(self, request, sku_id):
        """
        获取订单评论信息并返回
        :param request:
        :param sku_id:
        :return:
        """
        # 1.获取参数
        try:
            goods = OrderGoods.objects.filter(
                sku_id=sku_id, is_commented=True).order_by('-create_time')[:30]
        except OrderGoods.DoesNotExist:
            return http.HttpResponseForbidden('sku_id 参数错误')
        # 2.校验参数

        # 3.链接数据库
        comment_list = []
        for good in goods:
            username = good.order.user.username
            comment_list.append({
                'username': username[0] + '****' + username[-1] if good.is_anonymous else username,
                'comment': good.comment,
                'score': good.score,
            })
        # 4.查询数据
        # 5.拼接数据返回
        context = {
            'code': RETCODE.OK,
            'errmsg': 'ok',
            'goods_comment_list': comment_list,

        }
        return http.JsonResponse(context)


class DetailVisitView(View):
    """统计分类商品访问量"""

    def post(self, request, category_id):
        """
        统计商品用户的访问量
        :param request:
        :param category_id:
        :return:
        """
        # 先根据category_id获取当前的类别
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('缺少必传参数')

        # 1.获取今天的时间
        t = timezone.localtime()  # 获取时间对象
        # 根据时间对象拼接日期的字符串形式
        today_str = '%d-%02d-%02d' % (t.year, t.month, t.day)
        # 将字符串转为日期格式
        today_date = datetime.datetime.strptime(today_str, '%Y-%m-%d')
        # 2.在数据库中进行查询看当前商品是否有被浏览过
        try:
            counts_data = GoodsVisitCount.objects.get(date=today_date, category=category)
        # 3.如果有就进行加一
        except GoodsVisitCount.DoesNotExist:
            counts_data = GoodsVisitCount()
        try:
            # 4.如果没有就新建记录并保存
            counts_data.category = category
            counts_data.count += 1
            counts_data.date = today_date
            counts_data.save()
        except Exception as e:
            logger.error(e)
            return http.HttpResponseForbidden('数据保存失败')
        # 5.返回
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK'})


class DetailView(View):
    """商品详情页"""

    def get(self, request, sku_id):
        """
        获取商品详情页
        :param request:
        :param sku_id:
        :return:
        """
        # 获取商品频道分类
        categories = get_categories()
        sku = SKU.objects.get(id=sku_id)
        category = sku.category
        # 获取商品sku规格
        data = get_goods_and_spec(sku_id, request)

        # 根据商品类别id获取商品导航页
        breadcrumb = get_breadcrumb(category)
        # 组合参数
        context = {
            'categories': categories,
            'goods': data.get('goods'),
            'sku': data.get('sku'),
            'specs': data.get('goods_specs'),
            'breadcrumb': breadcrumb,
        }
        # 进行返回
        return render(request, 'detail.html', context=context)


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
