from django import forms
from django.contrib.auth.models import User
from .models import Profile
class UserLoginForm(forms.Form):
    # username = forms.CharField()
    # password = forms.CharField()
    username = forms.CharField(label="fas fa-user", max_length=30, widget=forms.TextInput(attrs={'class': 'text-white form-control input-text', 'placeholder':'用户名'}))
    password = forms.CharField(label="fas fa-lock", max_length=30, widget=forms.PasswordInput(attrs={'class': 'text-white form-control input-text', 'placeholder':'密码'}))
# 注册用户表单
class UserRegisterForm(forms.ModelForm):
    # 复写 User 的密码
    password = forms.CharField()
    password2 = forms.CharField()
    class Meta:
        model = User
        fields = ('username', 'email')


    def clean_password2(self):
        data = self.cleaned_data
        if data.get('password') == data.get('password2'):
            return data.get('password')
        else:
            raise forms.ValidationError("密码输入不一致，请重新输入。")
class ProfileFrom(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('phone', 'avatar', 'bio')