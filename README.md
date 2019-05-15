# 美多商城项目

>1.前端框架:Vue

>2.后端框架:Django&Jinja2

>3.项目配置步骤:

    1.仓库创建项目

    2.clone本地

    3.进到项目目录,创建虚拟环境

    4.安装django==1.11.11 创建jango项目meiduo,django-admin startproject meiduo

    5.用pycharm打开项目目录进行配置

    6.先配解释器,再把settings文件移到settings目录里面,在manager里面进行相关的设置,运行也要进行配置,配置完启动测试

    7.配置jinja2模板,先下载,下载后dev里面配置,同名目录下创建utils里面创建jinja2_env进行环境的配置

    8.mysql的配置,创建数据库,创建用户,施加权限,更新设置,同名目录下的init文件进行初始化mysqldb(),配置完启动测试

    9.redis的配置,下载jango-redis,在dev里面配置redis,注意路径

    10.静态路径的配置,在dev里面配置static,staticfiles_dirs=列表,同名目录下添加templates,在dir下配置

    11.日志文件的配置,在dev里面进行配置

    12.创建子应用用户,实现用户注册,所有应用创建在apps下,统一注册应用,创建导包路径

    13.创建注册接口,实现模板的渲染,添加用户模型,继承于AbstractUser
    
    14.在dev中再配置一句 AUTH_USER_MODEL = 'users.User' 让django知道你重写了User,最后进行模型的迁移,完成初步的配置
