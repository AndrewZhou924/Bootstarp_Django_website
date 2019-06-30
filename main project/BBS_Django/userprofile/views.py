from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from .forms import UserLoginForm, UserRegisterForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import ProfileFrom
from .models import Profile
from django.contrib import messages

def user_login(request):
    # 点击登录
    if request.method == 'POST':
        user_login_form = UserLoginForm(data=request.POST)
        if user_login_form.is_valid():
            data = user_login_form.cleaned_data

            # 检验账号、密码是否正确匹配数据库中的某个用户
            # 如果均匹配则返回这个 user 对象
            user = authenticate(username=data['username'], password=data['password'])
            if user:
                login(request, user)

                # 增加sesson去保存一些用户信息
                request.session['is_login'] = True
                request.session['user_id'] = user.id
                request.session['user_name'] = user.username

                return redirect("article:article_list")
                # return render(request, 'article/login.html', locals())
                # return render(request, 'userprofile/login.html', locals())
            else:
                messages.error(request, "账号或密码有误！")
                # message = "账号或密码有误！"
                # user_login_form = UserLoginForm()
                # context = {'userprofile': data, 'user_login_form': UserLoginForm}
                # return redirect('userprofile:login')
                return render(request, 'userprofile/login.html', locals())
                #return HttpResponse("账号或密码输入错误，请重新输入！")
        else:
            messages.error(request, "账号或密码输入不合法")
            # return redirect('userprofile:login')
            return render(request, 'userprofile/login.html', locals())


    user_login_form = UserLoginForm()
    return render(request, 'userprofile/login.html', locals())

def user_logout(request):
    logout(request)
    request.session.flush()
    
    # 重定向到登录界面
    return redirect("userprofile:login")

def user_register(request):
    if request.method =='POST':
        user_register_form = UserRegisterForm(data=request.POST)
        
        if user_register_form.is_valid():

            # 检查两次密码输入是否一致
            password = user_register_form.cleaned_data['password']
            password2 = user_register_form.cleaned_data['password2']
            if password != password2:
                messages.error(request, "两次输入密码不一致！")
                user_register_form = UserRegisterForm(data=request.POST)
                context = {'form': user_register_form}
                return render(request, 'userprofile/register.html', locals())

            new_user = user_register_form.save(commit=False)
            new_user.set_password(user_register_form.cleaned_data['password'])
            new_user.save()
            login(request, new_user)
            return redirect("article:article_list")
        else:
            messages.error(request, "您的输入有误，请重新输入")
            user_register_form = UserRegisterForm(data=request.POST)
            context = {'form': user_register_form}
            return render(request, 'userprofile/register.html', locals())

    user_register_form = UserRegisterForm
    return render(request, 'userprofile/register.html', locals())



@login_required(login_url='/userprofile/login/')
def user_delete(request,id):
    user = User.objects.get(id=id)
    if request.user == user:
        logout(request)
        user.delete()
        return  redirect('article:article_list')
    else:
        return HttpResponse("你没有权限删除")


#编辑用户信息
@login_required(login_url='/userprofile/login/')
def profile_edit(request, id):
    user = User.objects.get(id=id)
    #user_id OneToOneField 是自动生成的字段
    profile = Profile.objects.get(user_id=id)

    if request.method == "POST":
        #验证修改数据者
        if request.user != user:
            return HttpResponse("你没有权限修改此用户信息")
        profile_form = ProfileFrom(request.POST, request.FILES)
        if profile_form.is_valid():
            profile_cd = profile_form.cleaned_data
            profile.phone = profile_cd['phone']
            profile.bio = profile_cd['bio']

            if 'avatar' in request.FILES:
                profile.avatar = profile_cd["avatar"]

            profile.save()
            messages.info(request,"信息更新成功")
            return redirect("userprofile:edit",id=id)
        else:
            # 未触发。暂时无法验证问题
            messages.error(request, "表单内容有误，请重新填写！")
            context = {'profile': profile, 'profile_form': ProfileFrom}
            return render(request, 'userprofile/edit.html', context)
            return HttpResponse("注册表单输入有误，请重新输入~")

    elif request.method == "GET":
        profile_form = ProfileFrom()
        context = {'profile_form': profile_form, 'profile':profile, 'user':user}
        return render(request,'userprofile/edit.html',context)
    else:
        return HttpResponse("请使用GET/POST请求数据")



