from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user1 = User.objects.create_user(username='not_author')
        cls.group = Group.objects.create(
            title='Тестова группа',
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
        self.authorized_client1 = Client()
        self.authorized_client1.force_login(self.user1)

    def test_pages_accessible_anyone(self):
        """Проверка доступности страниц для guest_client."""
        pages = {
            '/': HTTPStatus.OK,
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            f'/profile/{self.user.username}/': HTTPStatus.OK,
            f'/posts/{self.post.pk}/': HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for adress, response in pages.items():
            with self.subTest(adress=adress):
                status_code = self.guest_client.get(adress).status_code
                self.assertEqual(status_code, response)

    def test_pages_accessible_authorized_client(self):
        """Проверка доступности страниц для authorized_client"""
        pages = {
            '/create/': HTTPStatus.OK,
            f'/posts/{self.post.pk}/edit/': HTTPStatus.OK,
        }
        for adress, response in pages.items():
            with self.subTest(adress=adress):
                status_code = self.authorized_client.get(adress).status_code
                self.assertEqual(status_code, response)

    def test_urls_uses_correct_template(self):
        """Проверка использования URL-адресами правильных HTML-шаблонов."""
        urls_adress = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            f'/posts/{self.post.pk}/edit/': 'posts/post_create.html',
            '/create/': 'posts/post_create.html',
        }
        for adress, templates in urls_adress.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, templates)

    def test_create_edit_pages_inaccessible_guest_client(self):
        """
        Проверка недоступности страниц create,
        edit и add_comment для guest_client"""
        pages = {
            '/create/': HTTPStatus.FOUND,
            f'/posts/{self.post.pk}/edit/': HTTPStatus.FOUND,
            f'/posts/{self.post.pk}/comment/': HTTPStatus.FOUND,
        }
        for adress, response in pages.items():
            with self.subTest(adress=adress):
                status_code = self.guest_client.get(adress).status_code
                self.assertEqual(status_code, response)

    def test_edit_page_inaccessible_not_author_authorized_client(self):
        """
        Проверка недоступности страницы edit
        для authorized_client не автора
        """
        response = self.authorized_client1.get(
            f'/posts/{self.post.pk}/edit/'
        ).status_code
        self.assertEqual(response, HTTPStatus.FOUND)
