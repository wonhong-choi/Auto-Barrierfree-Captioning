from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(PostForm, self).__init__(*args, **kwargs)
        if user:
            self.initial['author'] = user.id
            self.fields['author'].widget = forms.HiddenInput()

        # Modify CSS classes for form fields
        self.fields['title'].widget.attrs['class'] = 'form-control my-input'
        self.fields['content'].widget.attrs['class'] = 'form-control my-textarea'
        self.fields['file'].widget.attrs['class'] = 'form-control my-file-input'

    class Meta:
        model = Post
        fields = ['title', 'content', 'author', 'file', 'language']
        labels = {
            'title': '제목',
            'content': '내용',
            'file': '파일',
        }
        
class VideoForm(forms.Form):
    file = forms.FileField()