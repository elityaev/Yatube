from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Post, Group

User = get_user_model()


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache_index_page(self):
        cache1 = self.guest_client.get('/').content
        Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=self.group,
        )
        cache2 = self.guest_client.get('/').content
        self.assertEqual(cache1, cache2)
        cache.clear()
        self.assertNotEqual(cache2, self.guest_client.get('/').content)
