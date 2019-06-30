from django import forms
from django.contrib.auth.models import User
from .models import Profile
from django.contrib import messages
import os

class UserLoginForm(forms.Form):
    # username = forms.CharField()
    # password = forms.CharField()
    username = forms.CharField(label="fas fa-user", max_length=30, widget=forms.TextInput(attrs={'class': 'text-white form-control input-text', 'placeholder':'用户名'}))
    password = forms.CharField(label="fas fa-lock", max_length=30, widget=forms.PasswordInput(attrs={'class': 'text-white form-control input-text', 'placeholder':'密码'}))

# 注册用户表单
class UserRegisterForm(forms.ModelForm):
    # 复写 User 的密码
    password = forms.CharField(label="fas fa-lock", max_length=30, widget=forms.PasswordInput(attrs={'class': 'text-white form-control input-text', 'placeholder':'设置密码，不多于30字'}))
    password2 = forms.CharField(label="fas fa-lock", max_length=30, widget=forms.PasswordInput(attrs={'class': 'text-white form-control input-text', 'placeholder':'确认密码'}))
    class Meta:
        model = User
        fields = ('username', 'email')

        labels = {
            'username': "fas fa-user",
            'email': "fas fa-envelope"
        }

        max_lengths ={
            'username': 30,
            'email': 50
        }

        widgets = {
            'username': forms.TextInput(attrs={'class': 'text-white form-control input-text','placeholder':'设置用户名，不多于30字'}),
            'email': forms.TextInput(attrs={'class': 'text-white form-control input-text','placeholder':'设置安全邮箱'})
        }

    # def clean_password2(self):
    #     data = self.cleaned_data
    #     if data.get('password') == data.get('password2'):
    #         return data.get('password')
    #     else:
    #         raise forms.ValidationError("密码输入不一致，请重新输入。")
            
# # 设置头像的上传路径，以免发生文件命名冲突
# # 每个用户的头像文件命名为 [username].jpg
# BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media/avatar')
# def upload_to(instance, fielname):
#     path = '/'.join(['avatar', instance.user.username])
#     path +='/'

#     # 清除原来的头像图片
#     remove_path = '/'.join([MEDIA_ROOT, instance.user.username])
#     if os.path.exists(remove_path):
#         os.remove(remove_path) 
#     return path

class ProfileFrom(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ('phone', 'avatar', 'bio')
