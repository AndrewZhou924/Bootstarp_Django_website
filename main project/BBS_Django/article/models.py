from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
import os
from DjangoUeditor.models import UEditorField

# 设置头像的上传路径，以免发生文件命名冲突
# 每个用户的头像文件命名为 [username].jpg
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/articleContent/')
def upload_to(instance, fielname):
    return '/'.join([MEDIA_ROOT, instance.user.username, '%Y%m%d'])

class ArticlePost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)

    body = UEditorField(width=600, height=300, toolbars="full", imagePath="images/", filePath="files/",
                            upload_settings={"imageMaxSize": 4096000,
                            "imagePathFormat":"image/ueditor/%Y%m/%(basename)s_%(datetime)s.%(extname)s"},
                            settings={}, verbose_name='内容')

    created = models.DateTimeField(default=timezone.now)
    update = models.DateTimeField(auto_now=True)

    # 总浏览数和点赞数
    total_views = models.PositiveIntegerField(default=0)
    likes  = models.PositiveIntegerField(default=0)

    # 新的属性
    author_avatar = models.ImageField(default='')
    catagory = models.CharField(max_length=100,default='')
    content_img = models.ImageField(upload_to=upload_to,default='')
    brief = models.CharField(max_length=500,default='')

    class Meta:
        ordering = ('-created',)
    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse('article:article_detail', args=[self.id])