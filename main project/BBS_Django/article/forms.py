from django import  forms
from .models import ArticlePost


class ArticlePostForm(forms.ModelForm):
    class Meta:
        model = ArticlePost
        
        # TODO 增加文章分类
        # fields = ('title', 'body', 'catagory')
        fields = ('title', 'body')

        
