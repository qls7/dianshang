from django.contrib.auth.decorators import login_required


class LoginRequiredMixin(object):
    """验证用户是否已登录的扩展类"""
    @classmethod
    def as_view(cls, **initkwargs):
        """
        验证用户是否登录
        :param initkwargs:
        :return:
        """
        view =super().as_view()
        return login_required(view)
