from django import forms
from reply.models import Reply

class ReplyForm(forms.ModelForm):            
    class Meta:
        model = Reply
        fields = ('contents', 'author')
        exclude = ('author',)