from django import forms

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
