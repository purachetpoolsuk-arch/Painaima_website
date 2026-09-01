from django import forms
from django.contrib.auth.models import User
from .models import Profile


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-input", "placeholder": "ชื่อผู้ใช้ (Username)"}),
            "email": forms.EmailInput(attrs={"class": "form-input", "placeholder": "อีเมล (Email)"}),
        }


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["full_name", "avatar", "bio", "location", "website"]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-input", "placeholder": "ชื่อ-นามสกุล หรือชื่อแสดง"}),
            "bio": forms.Textarea(attrs={"class": "form-input", "rows": 3, "placeholder": "บอกเล่าเกี่ยวกับตัวคุณสั้นๆ..."}),
            "location": forms.TextInput(attrs={"class": "form-input", "placeholder": "เช่น กรุงเทพฯ, เชียงใหม่, ภูเก็ต"}),
            "website": forms.URLInput(attrs={"class": "form-input", "placeholder": "https://yourwebsite.com"}),
            "avatar": forms.FileInput(attrs={"class": "form-file-input", "accept": "image/*", "id": "avatar-file-input"}),
        }
