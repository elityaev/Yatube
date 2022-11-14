from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from .models import Group, Post, User, Follow
from .forms import PostForm, CommentForm
from .pagination import pagination


@cache_page(60)
def index(request):
    """Отображение главной страницы."""
    posts = Post.objects.all()
    page_obj = pagination(posts, request)
    context = {
        'page_obj': page_obj,
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
    """Отображение страницы поста."""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm()
    comments = post.comments.all()
    counter = post.author.posts.count()
    context = {
        'post': post,
        'form': form,
        'comments': comments,
        'counter': counter
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
