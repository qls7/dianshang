from django.conf.urls import url

from areas import views

urlpatterns = [
    # 省
    url(r'^areas/$',views.ProvinceAreasView.as_view(),name='province'),
    # 子级地区
    url(r'^areas/(?P<pk>[1-9]\d+)/$', views.SubAreasView.as_view(),name='sub'),
]