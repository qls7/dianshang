from django.conf.urls import url
from . import views
urlpatterns =[
    # 购物车查询和新增和修改和删除
    url(r'^carts/$', views.CartsView.as_view(), name='info'),
]