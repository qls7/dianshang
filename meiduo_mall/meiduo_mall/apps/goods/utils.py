from collections import OrderedDict

from goods.models import GoodsChannel, GoodsCategory


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
