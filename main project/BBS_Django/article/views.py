# 引入redirect重定向模块
from django.shortcuts import render, redirect
import markdown
from .models import ArticlePost
# 引入刚才定义的ArticlePostForm表单类
from .forms import ArticlePostForm
# 引入HttpResponse
from django.contrib import messages
from django.http import HttpResponse,HttpResponseRedirect
# 引入User模型
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from userprofile.models import Profile
from django.core.paginator import Paginator
from django.db.models import Q
from comment.models import Comment
from userprofile.models import Profile

# 列表页  --翻页
def article_list(request):
    search  = request.GET.get('search')
    order = request.GET.get('order')
    
    # 如果是搜索模式
    if search:
        # 排序方式是“最热”
        if order == 'total_views':
            article_list = ArticlePost.objects.filter(
                Q(title__icontains=search)|
                Q(body__icontains=search)
            ).order_by('-total_views')
        else: # 排序方式是“最新”
            article_list = ArticlePost.objects.filter(
                Q(title__icontains=search)|
                Q(body__icontains=search)
            )
    else: # 不是搜索模式，即显示所有文章
        search = ""
        if order == 'total_views':
            article_list = ArticlePost.objects.all().order_by('-total_views')
        else:
            article_list = ArticlePost.objects.all()

    pagintor = Paginator(article_list,3)
    # 获取页码
    page = request.GET.get('page')
    # 页码内容反个 articles
    articles = pagintor.get_page(page)

    # TODO 增加md格式支持
    context = {'articles':articles, 'order':order,}
    return render(request,'article/list.html',context)

# 个人主页：列表页  --翻页
# id - user_id
# TODO test this function
def personal_article_list(request, id):
    search  = request.GET.get('search')
    order = request.GET.get('order')
    user = User.objects.get(id=id)
    user_name = user.username
    
    # 如果是搜索模式
    if search:
        # 排序方式是“最热”
        if order == 'total_views':
            article_list = ArticlePost.objects.filter(
                Q(title__icontains=search)|
                Q(body__icontains=search)
            ).order_by('-total_views')
        else: # 排序方式是“最新”
            article_list = ArticlePost.objects.filter(
                Q(title__icontains=search)|
                Q(body__icontains=search)
            )
    else: # 不是搜索模式，即显示所有文章
        search = ""
        if order == 'total_views':
            article_list = ArticlePost.objects.filter(Q(author__username=user_name)).order_by('-total_views')
        else:
            article_list = ArticlePost.objects.filter(Q(author__username=user_name))

    pagintor = Paginator(article_list,3)
    # 获取页码
    page = request.GET.get('page')
    # 页码内容反个 articles
    articles = pagintor.get_page(page)

    # TODO 增加一个新的html模板
    return render(request,'article/list.html',context)


# TODO test this function
def article_addLikes(request, id):
    article = ArticlePost.objects.get(id=id)
    article.likes += 1
    article.save(update_fields=['likes'])

# 点进去阅读文章内容，支持markdown格式显示
def article_detail(request, id):
    article = ArticlePost.objects.get(id=id)
    comments = Comment.objects.filter(article=id)
    article.total_views += 1
    article.save(update_fields=['total_views'])

    md = markdown.Markdown(
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
        ]
    )
    article.body = md.convert(article.body)

    # 新增了md.toc对象
    context = {'article': article, 'toc': md.toc, 'comments':comments}

    return render(request, 'article/detail.html', context)
    

from django.forms import forms
# from DjangoUeditor.models import UEditorField
from DjangoUeditor.forms import UEditorField
class TestUEditorForm(forms.Form):
    content = UEditorField('内容', width=600, height=300, toolbars="full", imagePath="images/", filePath="files/",
                           upload_settings={"imageMaxSize": 1204000},
                           settings={})
# 创建文章，前提是必须已经登录
@login_required(login_url='/userprofile/login/')
def article_create(request):
    # 判断用户是否提交空数据
    if request.method == "POST":
        # 将提交的数据复制到表单
        article_post_from = ArticlePostForm(data=request.POST)
        # 判断提交的数据是否满足模型要求
        if article_post_from.is_valid():
            # 保存数据但不提交到数据库
            new_article = article_post_from.save(commit=False)
            # 指定数据库中 id 为1的用户为作者
            # 如果你进行过删除数据表的操作，可能会找不到id=1的用户
            # 此时请重新创建用户，并传入此用户的id
            new_article.author = User.objects.get(id=request.user.id)
            # 将文章保存到数据库

            # TODO get user avatar
            user = request.session.get('user', None)
            user_profile = Profile.objects.get(user = request.user)
            new_article.author_avator = user_profile.avatar

            # TODO test upload picture


            new_article.save()
            # 返回文章列表
            return redirect("article:article_list")
        else:
            messages.error(request, "表单内容有误，请重新填写！")
            return render(request, 'article/create.html')
            # article_post_form = ArticlePostForm()
            # context = {'article_post_form': article_post_form}
            # return HttpResponse("表单内容有误，请重新填写！")

    else:
        # 创建表单类实例
        
        # # 赋值上下文
        # context = {'article_post_form': article_post_from}
        # # 返回模板
        # return render(request, 'article/create.html',context)

        # article_post_from = TestUEditorForm()
        article_post_from = ArticlePostForm()
        return render(request, 'article/create.html', {'form': article_post_from})

# 删除文章，前提是必须已经登录
@login_required(login_url='/userprofile/login/')
def article_delete(request, id):

    # 记住来源的url，如果没有则设置为首页('/')
    # request.session['last_page'] = request.META.get('HTTP_REFERER', '/')
    user = request.session.get('_auth_user_id')
    # 根据id获取文章
    article = ArticlePost.objects.get(id=id)
    if request.user != article.author:
        messages.error(request, "你没有权限删除此文章")
        # return redirect("article:article_list")
        article_post_form = ArticlePostForm()
        context = {'article': article, 'article_post_form': article_post_form}
        return render(request, 'article/detail.html', context)
    else:
        # 调用.delete方法删除
        article.delete()
    return redirect("article:article_list")

# 更新文章，前提是必须已经登录
@login_required(login_url='/userprofile/login/')
def article_update(request,id):
    """
        更新文章的视图函数
        通过POST方法提交表单，更新titile、body字段
        GET方法进入初始表单页面
        id： 文章的 id
    """
    user = request.session.get('_auth_user_id')

    article = ArticlePost.objects.get(id=id)
    #print(user,article.author_id)
    if request.user != article.author:
    # if str(article.author_id) != str(user):
        messages.error(request, "你没有权限修改此文章")
        article_post_form = ArticlePostForm()
        context = {'article': article, 'article_post_form': article_post_form}
        return render(request, 'article/detail.html', context)

    if request.method == "POST":
        # if str(article.author_id) != str(user):
        #     messages.error(request, "你没有权限修改此文章")
        #     article_post_form = ArticlePostForm()
        #     context = {'article': article, 'article_post_form': article_post_form}
        #     return render(request, 'article/detail.html', context)
        #     #return HttpResponse("你没有权限修改此文章")
        article_post_form = ArticlePostForm(data=request.POST)
        if article_post_form.is_valid():
            article.title = request.POST['title']
            article.body = request.POST['body']
            article.save()
            return redirect("article:article_detail",id=id)
        else:
            messages.error(request, "表单内容有误，请重新填写！")
            context = {'article': article, 'article_post_form': article_post_form}
            return render(request, 'article/update.html',context)


    else:
        article_post_form = ArticlePostForm()
        context = {'article': article, 'article_post_form': article_post_form}
        return render(request, 'article/update.html', context)
# def return_to_list(request):
#     return redirect("article:article_list")
