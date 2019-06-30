from django import  forms
from .models import ArticlePost


class ArticlePostForm(forms.ModelForm):
    title  = forms.CharField(label="fas fa-lock", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control input-text', 'placeholder':'题目'}))
        
    class Meta:
        model = ArticlePost
        
        # TODO 增加文章分类
        # fields = ('title', 'body', 'catagory')
        # fields = ('title', 'body')
        fields = ('body',)
        