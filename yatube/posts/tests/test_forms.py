import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Post, Group, Comment

TEMP_MEDIA_ROOT = tempfile.mktemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='auth')
        cls.user2 = User.objects.create_user(username='auth2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост1',
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user2,
            text='Тестовый комментарий',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)

    def _assert_posts_equal(self, expected_post, actual_post):
        fields_list = ['text', 'pub_date', 'author', 'group', 'image']
        for field in fields_list:
            self.assertEqual(
                getattr(expected_post, field),
                getattr(actual_post, field)
            )

    def test_image_in_context_paginated_pages(self):
        """
        Появление поста с картинкой на страницах
        index, group_list, profile"""
        addresses = {
            reverse('posts:index'): self.post,
            reverse(
                'posts:group_list', kwargs={
                    'slug': self.group.slug
                }
            ): self.post,
            reverse(
                'posts:profile', kwargs={
                    'username': self.user.username
                }
            ): self.post,
        }
        for address, post in addresses.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                first_object = response.context['page_obj'][0]
                self._assert_posts_equal(first_object, post)

    def test_image_in_context_post_detail(self):
        """Появление поста с картинкой на странице post_detail"""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.pk}
            )
        )
        object_context = response.context['post']
        self._assert_posts_equal(object_context, self.post)

    def test_create_post(self):
        """ Валидная форма создает запись."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост2',
            'group': self.group.pk,
            'image': self.uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:profile', kwargs={'username': self.user.username}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(
            author=self.user,
            text='Тестовый пост2',
            group=self.post.group.pk,
            image='posts/small.gif'
        ).exists())

    def test_post_edit(self):
        """Валидная форма редактирует запись"""
        form_data = {
            'text': 'Отредактированный пост',
            'group': self.group.pk
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.post.refresh_from_db()
        self.assertEqual(self.post.text, 'Отредактированный пост')
        self.assertRedirects(
            response, reverse(
                'posts:post_detail', kwargs={'post_id': self.post.pk}
            )
        )

    def test_create_comment(self):
        """ Валидная форма создает комментарий."""
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий2',
        }
        response = self.authorized_client2.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:post_detail', kwargs={'post_id': self.post.pk}
            )
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(Comment.objects.filter(
            post=self.post,
            author=self.user2,
            text='Тестовый комментарий2',
        ).exists())
