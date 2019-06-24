from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

class ArticlePost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    body = models.TextField()
    created = models.DateTimeField(default=timezone.now)
    update = models.DateTimeField(auto_now=True)

    # 总浏览数和点赞数
    total_views = models.PositiveIntegerField(default=0)
    likes  = models.PositiveIntegerField(default=0)

    # TODO
    # catagory = models.CharField(max_length=100)
    # content_img = models.ImageField(upload_to='uploadPictures/%Y%m%d/')
    # author_avator = models.ImageField()
    # author_avator_url is better?

    class Meta:
        ordering = ('-created',)
    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse('article:article_detail', args=[self.id])