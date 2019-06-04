#!/home/python/.virtualenvs/meiduo_mall/bin/python3
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings.dev")

import django
django.setup()


# 获取商品频道分类
import os

from django.conf import settings
from django.core.cache import cache
from django.template import loader

from goods.models import SKU
from goods.utils import get_categories, get_goods_and_spec


def generate_static_sku_detail_html(sku_id):
    """
    生成静态商品详情页
    :param sku_id: 商品sku id
    :return:
    """
    categories = get_categories()
    # 获取商品sku规格

    sku = SKU.objects.get(id=sku_id)
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

    # 组合参数
    context = {
        'categories': categories,
        'goods': data.get('goods'),
        'sku': data.get('sku'),
        'specs': data.get('goods_specs')
    }
    # 进行返回
    template = loader.get_template('detail.html')
    html_text = template.render(context)
    file_path = os.path.join(settings.STATICFILES_DIRS[0], 'detail/'+str(sku_id)+'.html')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_text)

if __name__ == '__main__':
    skus = SKU.objects.all()
    for sku in skus:
        print(sku.id)
        generate_static_sku_detail_html(sku.id)