from django.contrib import admin
from .models import ArticlePost

class ArticlePostAdmin(admin.ModelAdmin):
    fields = ['title', 'body']

# Register your models here.
admin.site.register(ArticlePost,ArticlePostAdmin)