from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client


User = get_user_model()


class UserURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_accessible(self):
        pages = {
            '/auth/signup/': HTTPStatus.OK,
            '/auth/login/': HTTPStatus.OK,
            '/auth/password_reset/': HTTPStatus.OK,
            '/auth/password_reset/done/': HTTPStatus.OK,
            '/auth/reset/done/': HTTPStatus.OK,
            '/auth/password_change/': HTTPStatus.OK,
            '/auth/password_change/done/': HTTPStatus.OK,
            '/auth/logout/': HTTPStatus.OK,
        }
        for adress, response in pages.items():
            with self.subTest(adress=adress):
                status_code = self.authorized_client.get(adress).status_code
                self.assertEqual(status_code, response)
