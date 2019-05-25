from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^register', views.RegisterView.as_view(), name='register'),
    # 判断用户名是否重复
    url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
    # 判断手机号是否重复
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
    # 登录
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    # 登出
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    # 用户中心
    url(r'^info/$', views.UserInfoView.as_view(), name='info'),
    # 添加邮箱
    url(r'^emails/$', views.EmailView.as_view(), name='add_email'),
    # 验证邮箱
    url(r'^emails/verification/$', views.VerifyEmailView.as_view(), name='verify_email'),
    # 地址页面展示路由:
    url(r'^addresses/$', views.AddressView.as_view(), name='address'),
    # 新增收货地址
    url(r'^addresses/create/$', views.CreateAddressView.as_view(),name='add_address'),
    # 修改和删除收货地址
    url(r'^addresses/(?P<address_id>\d+)/$', views.UpdateDestroyAddressView.as_view(),name='update_destroy'),
    # 设置默认地址
    url(r'^addresses/(?P<address_id>\d+)/default/$', views.DefaultAddressView.as_view(),name='default'),
    # 更新地址标题
    url(r'^addresses/(?P<address_id>\d+)/title/$', views.UpdateTitleAddressView.as_view(),name='title'),
    # 修改密码
    url(r'^password/$', views.ChangePasswordView.as_view(), name='pass'),
]
