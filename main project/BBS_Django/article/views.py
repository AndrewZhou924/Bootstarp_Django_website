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
import re

# 用于剔除html标签，从富文本中提取纯文本
def replaceCharEntity(htmlstr):
  CHAR_ENTITIES={'nbsp':' ','160':' ',
        'lt':'<','60':'<',
        'gt':'>','62':'>',
        'amp':'&','38':'&',
        'quot':'"','34':'"',}
    
  re_charEntity=re.compile(r'&#?(?P<name>\w+);')
  sz=re_charEntity.search(htmlstr)
  while sz:
    entity=sz.group()#entity全称，如>
    key=sz.group('name')#去除&;后entity,如>为gt
    try:
      htmlstr=re_charEntity.sub(CHAR_ENTITIES[key],htmlstr,1)
      sz=re_charEntity.search(htmlstr)
    except KeyError:
      #以空串代替
      htmlstr=re_charEntity.sub('',htmlstr,1)
      sz=re_charEntity.search(htmlstr)
  return htmlstr

# 用于剔除html标签，从富文本中提取纯文本
def filter_tag(htmlstr):  
    re_cdata = re.compile('<!DOCTYPE HTML PUBLIC[^>]*>', re.I)  
    re_script = re.compile('<\s*script[^>]*>[^<]*<\s*/\s*script\s*>', re.I) #过滤脚本  
    re_style = re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>', re.I) #过滤style  
    re_br = re.compile('<br\s*?/?>')  
    re_h = re.compile('</?\w+[^>]*>')  
    re_comment = re.compile('<!--[\s\S]*-->') 

    s = re_cdata.sub('', htmlstr)  
    s = re_script.sub('', s)  
    s=re_style.sub('',s)  
    s=re_br.sub('\n',s)  
    s=re_h.sub(' ',s)  
    s=re_comment.sub('',s)  
    blank_line=re.compile('\n+')  
    s=blank_line.sub('\n',s)  
    s=re.sub('\s+',' ',s)  
    s=replaceCharEntity(s)  

    if len(s) > 100:
        return s[:100]
    else:
        return s  

# 从富文本中获取第一张图片的url
def getFirstImageUrl(string):
  if "img src=" in string:
      candidate_str = string.split("img src=")[1]
      img_url = ""
      for char in candidate_str[1:]:
        if char == '"':
          break
        else:
          img_url += char
      return img_url
  else:
      return None

# TODO test this function
# 下拉加载更多
def article_list_getMore(search, order, bias, user_id):
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
    else: 
        if user_id >= 0:
            user = User.objects.get(id=id)
            user_name = user.username
            if order == 'total_views':
                article_list = ArticlePost.objects.filter(Q(author__username=user_name)).order_by('-total_views')
            else:
                article_list = ArticlePost.objects.filter(Q(author__username=user_name))
        else:
            if order == 'total_views':
                article_list = ArticlePost.objects.all().order_by('-total_views')
            else:
                article_list = ArticlePost.objects.all()

    # 目前设置每一页有3篇文章
    pagintor = Paginator(article_list,3)
    articles = pagintor.get_page(bias)
    context = {'articles':articles, 'order':order,}

    response = HttpResponse(context)
    return response


# 列表页  --翻页
def article_list(request):
    search  = request.GET.get('search')
    order = request.GET.get('order')
    catagory = request.GET.get('catagory')

    # 下拉加载更多
    bias = request.GET.get('bias')
    if bias and (bias>0):
            result = article_list_getMore(search, order, bias, user_id=-1)
            return result
    
    # 点赞 （增加点赞数）
    likes = request.GET.get('likes')
    article_id = request.GET.get('article_id')
    if likes and article_id:
        article_addLikes(article_id)

    # 按种类搜索    
    if catagory:
        article_list = ArticlePost.objects.filter(
                Q(title__icontains=search)|
                Q(body__icontains=search)|
                Q(catagory=catagory)
            )

    # 如果是搜索模式
    elif search:
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

    # 目前设置每一页有3篇文章
    pagintor = Paginator(article_list,9)
    # 获取页码
    page = request.GET.get('page')
    # 页码内容反个 articles
    articles = pagintor.get_page(page)

    context = {'articles':articles, 'order':order,}
    return render(request,'article/list.html',context)

# 个人主页：列表页  --翻页
# id - user_id
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
    context = {'articles':articles, 'order':order,}
    return render(request,'article/list.html',context)

# TODO test this function
def article_addLikes(id):
    article = ArticlePost.objects.get(id=id)
    article.likes += 1
    article.save(update_fields=['likes'])

# 点进去阅读文章内容，支持markdown格式显示
# id是user_id
def article_detail(request, id):
    article = ArticlePost.objects.get(id=id)
    comments = Comment.objects.filter(article=id).order_by('-created')
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
    
# 创建文章，前提是必须已经登录
@login_required(login_url='/userprofile/login/')
def article_create(request):
    # 判断用户是否提交空数据
    if request.method == "POST":
        # 将提交的数据复制到表单
        article_post_form = ArticlePostForm(data=request.POST)
        # 判断提交的数据是否满足模型要求
        if article_post_form.is_valid():
            # 保存数据但不提交到数据库
            new_article = article_post_form.save(commit=False)
            # 指定数据库中 id 为1的用户为作者
            # 如果你进行过删除数据表的操作，可能会找不到id=1的用户
            # 此时请重新创建用户，并传入此用户的id
            new_article.author = User.objects.get(id=request.user.id)
            # 将文章保存到数据库

            # get user avatar
            user = request.session.get('user', None)
            user_profile = Profile.objects.get(user = request.user)

            new_article.title = article_post_form.cleaned_data['title']
            new_article.author_avator = user_profile.avatar
            new_article.brief = filter_tag(new_article.body)
            new_article.content_img = getFirstImageUrl(new_article.body)

            new_article.save()
            # 返回文章列表
            return redirect("article:article_list")
        else:
            messages.error(request, "表单内容有误，请重新填写！")
            return render(request, 'article/create.html')

    else:
        article_post_form = ArticlePostForm()
        return render(request, 'article/create.html', {'form': article_post_form})

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
        messages.error(request, "你没有权限修改此文章")
        article_post_form = ArticlePostForm()
        context = {'article': article, 'article_post_form': article_post_form}
        return render(request, 'article/detail.html', context)

    if request.method == "POST":
        article_post_form = ArticlePostForm(data=request.POST)
        if article_post_form.is_valid():
            article.title = request.POST['title']
            article.body = request.POST['body']
            article.brief = filter_tag(article.body)
            article.content_img = getFirstImageUrl(article.body)
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
