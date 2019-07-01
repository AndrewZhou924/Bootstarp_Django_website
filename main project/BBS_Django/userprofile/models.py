from django.db import models
from django.contrib.auth.models import User
# 引入内置信号
from django.db.models.signals import post_save
# 引入信号接收器的装饰器
from django.dispatch import receiver
import os

# 设置头像的上传路径，以免发生文件命名冲突
# 每个用户的头像文件命名为 [username].jpg
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/avatar')
def upload_to(instance, fielname):
    path = '/'.join(['avatar', instance.user.username])
    path +='/'

    # 清除原来的头像图片
    remove_path = '/'.join([MEDIA_ROOT, instance.user.username])
    if os.path.exists(remove_path):
        os.remove(remove_path) 
    return path

# 用户扩展信息
class Profile(models.Model):
    # 与 User 模型构成一对一的关系
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # 电话号码字段
    phone = models.CharField(max_length=20, blank=True)
    # 头像
    avatar = models.ImageField(upload_to=upload_to, default='avatar/default.jpg')
#     avatar = models.ImageField(upload_to='avatar/%Y%m%d/', blank=True)
    # 个人简介
    bio = models.TextField(max_length=500, blank=True)
    # 大学信息
    university = models.TextField(max_length=100, default='')

    def __str__(self):
        return 'user {}'.format(self.user.username)


# 信号接收函数，每当新建 User 实例时自动调用
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# 信号接收函数，每当更新 User 实例时自动调用
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()