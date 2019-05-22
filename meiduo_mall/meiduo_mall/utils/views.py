from django import http
from django.contrib.auth.decorators import login_required

from meiduo_mall.utils.response_code import RETCODE
from django.utils.decorators import wraps  # wraps 的导入要手动导入


class LoginRequiredMixin(object):
    """验证用户是否已登录的扩展类"""

    @classmethod
    def as_view(cls, **initkwargs):
        """
        验证用户是否登录
        :param initkwargs:
        :return:
        """
        view = super().as_view()
        return login_required(view)


def login_required_json(view):
    """返回json格式的装饰器"""

    # wraps装饰器的目的是保持view函数原来的帮助说明
    # 即调用help(view)的时候打印出来的还是原来view的帮助说明,而不是装饰后的
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        # view(request,*args,**kwargs) view函数调用就需要这个参数

        # as_view()里面调用view(),view里面调用dispatch(),第一个参数必须是request

        # 判断是否登录
        if not request.user.is_authenticated():
            return http.JsonResponse({'code': RETCODE.USERERR, 'errmsg': '没有权限'})
        return view(request, *args, **kwargs)

    return wrapper


class LoginRequiredJSONMixin(object):
    """验证用户是否已登录的扩展类"""

    @classmethod
    def as_view(cls, **initkwargs):
        """
        验证用户是否登录
        :param initkwargs:
        :return:
        """
        view = super().as_view()
        return login_required_json(view)
