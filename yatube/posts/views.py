from django.core.mail import send_mail
from django.db.models import Count
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from taggit.models import Tag

from .models import Group, Post, User, Follow
from .forms import PostForm, CommentForm, EmailPostForm
from .pagination import pagination


@cache_page(60)
def index(request, tag_slug=None):
    """Отображение главной страницы, если передан tag_slug,
    отображается список постов с этим тегом."""
    posts = Post.objects.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = posts.filter(tags__in=[tag])
    page_obj = pagination(posts, request)
    context = {
        'page_obj': page_obj,
        'tag': tag
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Отображение страницы сообщества."""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = pagination(posts, request)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Отображение страницы профиля автора."""
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_obj = pagination(posts, request)
    context = {
        'author': author,
        'page_obj': page_obj,
    }
    if request.user.is_authenticated and Follow.objects.filter(
            author=author, user=request.user
    ).exists():
        context['following'] = True
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Отображение страницы поста, списка похожих
    статей (по тегам), добавление комментария."""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm()
    comments = post.comments.all()
    counter = post.author.posts.count()
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.objects.filter(
        tags__in=post_tags_ids
    ).exclude(id=post.id)
    similar_posts = similar_posts.annotate(
        same_tags=Count('tags')
    ).order_by('-same_tags', '-pub_date')[:3]
    context = {
        'post': post,
        'form': form,
        'comments': comments,
        'counter': counter,
        'similar_posts': similar_posts
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """
    Отображение страницы создания поста -
    только для зарегистрированных пользователей.
    """
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect('posts:profile', request.user)
    return render(request, 'posts/post_create.html', {'form': form})


@login_required
def post_edit(request, post_id):
    """
    Отображение страницы редактирования поста -
    только для автора поста.
    """
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    return render(
        request,
        'posts/post_create.html',
        {'form': form, 'is_edit': True}
    )


@login_required
def add_comment(request, post_id):
    """
    Добавление комментария к посту -
    только для зарегистрированных пользователей.
    """
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """
    Отображение страницы с постами автора, на которого подписан пользователь -
    только для зарегистрированных пользователей.
    """
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = pagination(posts, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Подписаться на автора."""
    following = get_object_or_404(User, username=username)
    if following != request.user:
        Follow.objects.get_or_create(
            user=request.user,
            author=following
        )
    return redirect('posts:profile', request.user)


@login_required
def profile_unfollow(request, username):
    """Отписаться от автора."""
    get_object_or_404(
        Follow, author__username=username, user=request.user
    ).delete()
    return redirect('posts:profile', request.user)


def post_share(request, post_id):
    """Отправка поста на почту."""
    post = get_object_or_404(Post, id=post_id)
    sent=False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolut_url())
            subject = f"{cd['name']} ({cd['email']}) рекомендует Вам прочесть {post}"
            message = f"Прочитайте \"{post}\" по ссылке {post_url}\n\n{cd['comments']}"
            send_mail(subject, message, cd['email'], [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    context = {'post': post, 'form': form, 'sent': sent}
    return render(request, 'posts/share.html', context)