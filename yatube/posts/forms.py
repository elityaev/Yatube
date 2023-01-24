from django import forms
from django.forms import Textarea

from .models import Post, Comment


class PostForm(forms.ModelForm):
    """Форма для создания поста."""
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст',
            'group': 'Группа',
        }
        help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться текст',
        }


class CommentForm(forms.ModelForm):
    """Форма для создания комментария."""
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Текст',
        }
        help_texts = {
            'text': 'Текст комментария'
        }


class EmailPostForm(forms.Form):
    """Форма для отправки поста на почту."""
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False, widget=Textarea)
