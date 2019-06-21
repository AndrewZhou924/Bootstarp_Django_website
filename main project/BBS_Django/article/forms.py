from django import  forms
from .models import ArticlePost


class ArticlePostForm(forms.ModelForm):
    class Meta:
        model = ArticlePost
        fields = ('title', 'body')

        # TODO 
        # fields = ('title', 'body', 'catagory')
