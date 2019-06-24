from django import  forms
from .models import ArticlePost


class ArticlePostForm(forms.ModelForm):
    class Meta:
        model = ArticlePost
        
        # TODO 
        # fields = ('title', 'body', 'catagory')
        # fields = ('title', 'body', 'content_img')
        fields = ('title', 'body')

        
