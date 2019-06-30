from django import  forms
from .models import ArticlePost


class ArticlePostForm(forms.ModelForm):
    title  = forms.CharField( max_length=100, widget=forms.TextInput(attrs={'class': 'form-control articletitle', 'placeholder':'不多于30字'}))
        
    class Meta:
        model = ArticlePost
        
        # TODO 增加文章分类
        # fields = ('title', 'body', 'catagory')
        # fields = ('title', 'body')
        fields = ('body',)
        