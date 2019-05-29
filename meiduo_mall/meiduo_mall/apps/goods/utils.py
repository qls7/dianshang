from collections import OrderedDict
from django.core.cache import cache
from django.shortcuts import render
from goods.models import GoodsChannel, GoodsCategory, SKU


# def get_goods_and_spec(sku_id,request):
#     """
#     获取当前sku的信息
#     :param sku_id:
#     :param request:
#     :return:
#     """
#     # 获取sku对应的goods(一个sku对应一个spu类)
#     try:
#         sku = SKU.objects.get(id=sku_id)
#         # 获取sku所有的图片,并保存到sku的属性中
#         sku.images =sku.skuimage_set.all()
#     except SKU.DoesNotExist:
#         return render(request,'404.html')
#     # 根据sku获取对应的所属商品的类
#     goods = sku.goods
#     # 根据goods获取对应的商品频道
#     goods.channel = goods.category1.goodschannel_set.all()[0]
#     # ########################################################
#
#     # 根据sku=3获取所有的规格(颜色4,内存5)(每一种规格都对应一个sku商品)
#     sku_specs = sku.skuspecification_set.order_by('spec_id')
#
#
#     # 存的是当前这个sku指定的选项(金色8,深色,灰色,64g11,256g)
#     sku_key = list() # (金色option.id=8,64g option.id=11)
#     for spec in sku_specs:
#         sku_key.append(spec.option.id)
#     # ########################################################
#
#     skus = goods.sku_set.all() # skus id 3-8
#
#     spec_sku_map = dict() # 组建一个规格和sku的映射的字典
#     for s in skus:
#         # 拿到每一个sku的规格的参数并通过规格id进行排序
#         s_specs = s.skuspecification_set.order_by('spec_id') # 先拿到id=3
#         # 再次组建字典的key和上面的sku_id的key再次重复组建
#         key = list()
#         # 第一次id = 3(金色option.id=8,64g option.id=11)
#         # 内层选项遍历完
#         for spec in s_specs:
#             key.append(spec.option.id)
#
#         #  把 id = 3(金色option.id=8,64g option.id=11) 放入键中,值为id = 3
#
#         spec_sku_map[tuple(key)] = s.id
#     # 内层结束一次后,第二次再来id=4,再次获取(金色option.id=8,256g option.id=12)再放入
#     # 以此类推,就会映射出一个选项id集合(金色8,256g11)=4 一直从3-8,有6个映射
#
#     # 获取当前商品类的所有商品的规格(以iphone手机为类,只有两种规格颜色,内存)
#     # sku_key的长度最少也要等于商品的规格,才能确定一种商品,
#     # 即最少也要一个颜色选项,一个内存选项
#     goods_specs = goods.goodsspecification_set.order_by('id')
#     # 如果小于说明是缺少规格参数的
#     if len(sku_key) < len(goods_specs):
#         return
#
#     # enumerate(枚举): 可以将一个可遍历的对象(元祖,列表,字符串等)组合成一个有索引的序列,
#     # 即取出索引,也取出值
#
#     for index,spec in enumerate(goods_specs): # 商品的规格只有2个颜色内存
#         # 复制一下本次sku的所有选项的id即键
#         key = sku_key[:] # 复制下这个sku的规格参数即(8,11)
#         # 获取该规格的所有选项
#         spec_options = spec.specificationoption_set.all()
#         # 第一次获取的是颜色选项,有三种颜色(金色8,深色9,灰色10)
#         # 第二次获取的是内存选项,有两种内存(64g11,256g12)
#         for option in spec_options:
#             # 第一次 key[0]即颜色赋值为金色8,
#             key[index] = option.id
#             # 给当前选项增加一个属性sku.id,并把映射里面对应的sku_id赋值给sku_id
#             option.sku_id = spec_sku_map.get(tuple(key))
#             # (8,11)=>8.sku_id
#             # (9,11)=>9.sku_id
#             # (10,11)=>10.sku_id
#             # (8,11)=>11.sku_id
#             # (8,12)=>12.sku_id
#         # 颜色遍历完之后,给当前规格增加一个属性,把这种颜色的所有选项赋值给规格的属性
#         spec.spec_options = spec_options
#         # 用户每次只能修改一个选项,每次修改选项,页面都会重新刷新,前端根据用户的选项不同,
#         # 发送不同的sku_id请求,再根据返回的sku获取价格和图片信息
#
#     data = {
#         'goods':goods,
#         'goods_specs':goods_specs,
#         'sku':sku,
#     }
#
#     return data
def get_goods_and_spec(sku_id, request):
    """
    获取产品的规格及商品类型
    :param request:
    :param sku_id:
    :return:
    """
    # 1.根据sku_id获取到sku
    # 2.根据sku获取到goods
    # 3.先把当前的sku对应的选项id存下
    # 4.根据goods获取所有的sku并生成选项id参数和sku.id一一对应的映射map
    # 5.根据goods获取所有的规格,按当前的sku的选项进行遍历
    # ,把sku.id存到选项的属性下,让前端可以进行遍历选项的时候就可以拿到sku_id
    # ,把每种规格的选项存到每种规格的属性下,让前端根据规格就可以获取属性,再根据属性的sku_id进行判断该选项是否对应sku
    # ,如果选项.sku_id有值并且等于当前的sku_id,则选中
    # ,如果选项.sku_id有值但不等于当前的sku_id,则增加超链接,用户点击的时候就重新发送请求
    # ,如果选项.sku_id没有值,说明当前选项还有没有存在的商品,不做任何操作,也可以注释这种情况,一般不会出现
    try:
        sku = SKU.objects.get(id=sku_id)
    except SKU.DoesNotExist:
        return render(request, '404.html')
    goods = sku.goods

    sku_specs = sku.skuspecification_set.all().order_by('spec_id')
    sku_key = list()
    for spec in sku_specs:
        sku_key.append(spec.option.id)

    skus = goods.sku_set.filter(is_launched=True)
    # 这里可以增加缓存,把每一类商品的map图存到缓存
    map = cache.get('goods' + str(goods.id))
    if map is None:
        sku_specs_option_sku_id_map = dict()
        for s in skus:
            s_specs = s.skuspecification_set.all().order_by('spec_id')
            s_key = list()
            for s_spec in s_specs:
                s_key.append(s_spec.option.id)
            sku_specs_option_sku_id_map[tuple(s_key)] = s.id
        cache.set('goods' + str(goods.id), sku_specs_option_sku_id_map, 3600)
    else:
        sku_specs_option_sku_id_map = map
    goods_specs = goods.goodsspecification_set.all().order_by('id')
    if len(sku_key) < len(goods_specs):
        return
    for index, spec in enumerate(goods_specs):
        key = sku_key[:]
        spec_options = spec.specificationoption_set.all().order_by('id')
        for option in spec_options:
            key[index] = option.id
            option.sku_id = sku_specs_option_sku_id_map.get(tuple(key))
        spec.spec_options = spec_options

    data = {
        'sku': sku,
        'goods_specs': goods_specs,
        'goods': goods,
    }
    return data


def get_categories():
    """
    获取商城商品分类菜单
    :return: 菜单字典
    """
    # 商品频道及分类菜单
    # 下面的代码生成的模板:
    # categories = {
    #  (1,  # 组1
    #       {'channels': [{'id': 1, 'name': '手机','url':'http://shouji.jd.com'},
    #                     {'id': 2, 'name': '相机','url':'http://www.itcast.cn'},
    #                     {'id': 3, 'name': '数码','url':'http://www.itcast.cn'}],
    #        'sub_cats': [ < GoodsCategory: 手机通讯 >,
    #                      < GoodsCategory: 手机配件 >,
    #                      < GoodsCategory: 摄影摄像 >,
    #                      < GoodsCategory: 数码配件 >,
    #                      < GoodsCategory: 影音娱乐 >,
    #                      < GoodsCategory: 智能设备 >,
    #                      < GoodsCategory: 电子教育 >
    #                    ]
    #       }
    #   ),(2, # 组2
    #        {
    #
    #   })
    # }
    # 1.定义一个有序字典
    categories = OrderedDict()
    # 2.先获取商品频道
    channels = GoodsChannel.objects.all().order_by('group_id', 'sequence')
    # 3.根据商品频道遍历获取每个channel
    for channel in channels:
        group_id = channel.group_id
        if group_id not in categories:
            categories[group_id] = {'channels': [], 'sub_cats': []}

        # 4.根据channel.category外键获取2级3级目录
        cat = channel.category
        # for cat in cats:
        categories[group_id]['channels'].append({
            'id': cat.id,
            'name': cat.name,
            'url': channel.url
        })
        sub = cat.goodscategory_set.all()
        # cat2.sub_cats = list()
        for cat2 in sub:
            cat2.sub_cats = list()
            # cat3 = cat2.goodscategory_set.all()
            for cat3 in cat2.goodscategory_set.all():
                cat2.sub_cats.append({
                    'id': cat3.id,
                    'name': cat3.name
                })
            categories[group_id]['sub_cats'].append({
                'id': cat2.id,
                'name': cat2.name,
                'sub_cats': cat2.sub_cats
            })
    # 5.返回
    return categories


def get_breadcrumb(category):
    """
    获取面包屑(导航页)
    :param category_id:
    :return:
    """
    # 定义一个字典,分别存储一级二级三级类
    breadcrumb = {
        'cat1': '',
        'cat2': '',
        'cat3': ''
    }
    # 根据category_id判断是一级类
    # category = GoodsCategory.objects.get(id=category_id)
    if category.parent is None:
        breadcrumb['cat1'] = category
    # 根据category_id判断是三级类
    elif category.goodscategory_set.all().count() == 0:
        breadcrumb['cat3'] = category
        breadcrumb['cat2'] = category.parent
        breadcrumb['cat1'] = category.parent.parent
    # 根据category_id判断是二级类
    else:
        breadcrumb['cat2'] = category
        breadcrumb['cat1'] = category.parent
    # 返回
    return breadcrumb
