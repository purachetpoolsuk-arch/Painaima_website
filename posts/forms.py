from django import forms
from .models import Post, Comment


class PostCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["image", "caption", "location"]
        widgets = {
            "image": forms.FileInput(attrs={
                "class": "form-file-input",
                "accept": "image/*",
                "id": "post-image-upload",
                "required": True,
            }),
            "caption": forms.Textarea(attrs={
                "class": "form-input",
                "rows": 4,
                "placeholder": "เขียนแคปชั่นของคุณ... เช่น วันนี้แวะมากินกาแฟร้านลับ #cafehopping #bkk @friend",
                "id": "post-caption-input",
            }),
            "location": forms.TextInput(attrs={
                "class": "form-input",
                "placeholder": "เพิ่มสถานที่ เช่น Siam Square One, เขาใหญ่, คาเฟ่อารีย์",
                "id": "post-location-input",
            }),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        widgets = {
            "text": forms.TextInput(attrs={
                "class": "comment-input",
                "placeholder": "เพิ่มความคิดเห็น...",
                "autocomplete": "off",
            })
        }
