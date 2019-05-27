from django.contrib import admin

# Register your models here.
from goods.models import Goods,SKU,SKUImage,SKUSpecification,SpecificationOption,GoodsCategory,GoodsChannel,GoodsSpecification

admin.site.register([
    Goods, SKU, SKUImage, SKUSpecification, SpecificationOption, GoodsCategory, GoodsChannel, GoodsSpecification

])