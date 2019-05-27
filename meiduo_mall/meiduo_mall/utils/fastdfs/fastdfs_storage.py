from django.conf import settings
from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client


class FastDFSStorage(Storage):
    """重写存储文件的save()"""
    def save(self, name, content, max_length=None):
        """
        重写上传文件的函数
        :param name:
        :param content:
        :param max_length:
        :return:
        """
        # 创建客户端对象
        client = Fdfs_client(settings.FDFS_CLIENT_CONF)
        # 调用函数进行上传
        result = client.upload_by_buffer(content.read())
        # 判断是否上传成功
        if result.get('Status') != 'Upload successed.':
            raise Exception('上传文件到FDFS系统失败')
        # 返回file_id
        file_id = result.get('Remote file_id')

        return file_id

    def exists(self, name):
        """重写exists方法"""
        return False

    def url(self, name):
        """重写url方法"""
        return settings.FDFS_URL + name
