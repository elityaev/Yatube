from itertools import islice

from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


from ..models import Post, Group, Comment, Follow

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def _assert_posts_equal(self, expected_post, actual_post):
        fields_list = ['text', 'pub_date', 'author', 'group']
        for field in fields_list:
            self.assertEqual(
                getattr(expected_post, field),
                getattr(actual_post, field)
            )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон в приложении posts."""
        templates_pages_name = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}): (
                'posts/group_list.html'
            ),
            reverse(
                'posts:profile', kwargs={'username': self.user.username}): (
                'posts/profile.html'
            ),
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}): (
                'posts/post_detail.html'
            ),
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}): (
                'posts/post_create.html'
            ),
        }
        for reverse_name, template in templates_pages_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_paginated_pages_show_correct_context(self):
        """
        Шаблоны index, group_list, profile
        сформированы с правильным контекстом.
        """
        addresses = {
            reverse('posts:index'): self.post,
            reverse(
                'posts:group_list', kwargs={
                    'slug': self.group.slug
                }): self.post,
            reverse(
                'posts:profile', kwargs={
                    'username': self.user.username
                }): self.post,
        }

        for address, post in addresses.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                first_object = response.context['page_obj'][0]
                self._assert_posts_equal(first_object, post)

    def test_post_detail_list_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        object_context = response.context['post']
        self._assert_posts_equal(object_context, self.post)

    def test_create_post_edit_list_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным типом полей."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_post_edit1_list_page_show_correct_context(self):
        """
        Шаблон post_detail сформирован с
        правильным контекстом(заполненные поля).
        """
        response = (self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}))
        )
        self.assertEqual(
            response.context['form'].initial['text'], self.post.text
        )
        self.assertEqual(
            response.context['form'].initial['group'], self.post.group.pk
        )

    def test_create_post_list_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным типом полей."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )

        batch_size = 20
        objs = (Post(
            author=cls.user,
            group=cls.group,
            text=f'Тестовый текст {i}'
        ) for i in range(13))
        while True:
            batch = list(islice(objs, batch_size))
            if not batch:
                break
            Post.objects.bulk_create(batch, batch_size)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_index_page_contains_ten_records(self):
        """Пагинатор 1-ой страницы index."""
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_index_page_contains_ten_records(self):
        """Пагинатор 2-ой страницы index."""
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_group_list_page_contains_ten_records(self):
        """Пагинатор 1-ой страницы group_list."""
        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_group_list_page_contains_ten_records(self):
        """Пагинатор 2-ой страницы group_list."""
        response = self.client.get(
            reverse('posts:group_list', kwargs={
                'slug': self.group.slug
            }) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_first_profile_page_contains_ten_records(self):
        """Пагинатор 1-ой страницы profile."""
        response = self.client.get(
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_profile_page_contains_ten_records(self):
        """Пагинатор 2-ой страницы profile."""
        response = self.client.get(
            reverse('posts:profile', kwargs={
                'username': self.user.username
            }) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)


class PostCreateTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group1 = Group.objects.create(
            title='Тестовая группа1',
            slug='test1',
            description='Тестовое описание',
        )

        cls.group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test2',
            description='Тестовое описание',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_availability_created_post_on_pages(self):
        """
        Появление созданного поста на страницах index,
        group_list, profile.
        """
        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=self.group1,
        )
        addresses = {
            reverse('posts:index'): post,
            reverse(
                'posts:group_list', kwargs={
                    'slug': self.group1.slug
                }
            ): post,
            reverse(
                'posts:profile', kwargs={
                    'username': self.user.username
                }
            ): post,
        }
        for address, post in addresses.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertIn(post, response.context['page_obj'])

    def test_post_create_another_group_list_page(self):
        """Отсутствие созданного поста на странице group_list другой группы."""
        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=self.group1,
        )
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group2.slug})
        )
        self.assertNotIn(post, response.context['page_obj'])

    def test_availability_created_comment_on_post_detail_page(self):
        """Появление созданного комментария на страницах post_detail."""
        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=self.group1,
        )
        comment = Comment.objects.create(
            post=post,
            author=self.user,
            text='Тестовый комментарий',
        )
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail', kwargs={'post_id': post.pk}
            )
        )
        self.assertIn(comment, response.context['comments'])


class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create_user(username='auth1')
        cls.user2 = User.objects.create_user(username='auth2')
        cls.user3 = User.objects.create_user(username='auth3')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user1)
        self.authorized_client3 = Client()
        self.authorized_client3.force_login(self.user3)

    def test_authorized_client_follow(self):
        """authorized_client может подписаться на автора."""
        self.authorized_client.post(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user2.username}
            )
        )
        self.assertTrue(Follow.objects.filter(
            user=self.user1,
            author=self.user2
        ).exists())

    def test_authorized_client_unfollow(self):
        """authorized_client может отписаться от автора."""
        Follow.objects.create(
            user=self.user1,
            author=self.user2
        )
        self.authorized_client.post(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.user2.username}
            )
        )
        self.assertFalse(Follow.objects.filter(
            user=self.user1,
            author=self.user2
        ).exists())

    def test_new_post_appears_subscribers_feed(self):
        """
        Новая запись появляется на странице подписчика
        и не появляется на странице не подписанного пользователя.
        """
        Follow.objects.create(
            user=self.user1,
            author=self.user2
        )
        post = Post.objects.create(
            author=self.user2,
            text='Тестовый пост',
            group=self.group
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertIn(post, response.context['page_obj'])
        response = self.authorized_client3.get(reverse('posts:follow_index'))
        self.assertNotIn(post, response.context['page_obj'])
