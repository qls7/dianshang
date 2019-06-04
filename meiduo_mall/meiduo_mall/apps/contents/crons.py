import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings.dev")

import django
django.setup()
from django.conf import settings
from django.template import loader

from contents.models import ContentCategory
from goods.utils import get_categories


def generate_static_index_html():
    """生成静态的主页html文件"""

    # 直接把静态页面的代码复制过来

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
        'categories': categories,
        'contents': content
    }

    # return render(request, 'index.html', context=context)
    # 分开进行返回,写入到文件中
    # 获取首页模板文件
    template = loader.get_template('index.html')
    # 渲染首页html字符串
    html_text = template.render(context)
    # 将首页html字符串写入到指定目录,命名'index.html'
    file_path = os.path.join(settings.STATICFILES_DIRS[0], 'index.html')
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_text)

if __name__ == '__main__':
    generate_static_index_html()