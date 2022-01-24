from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


User = get_user_model()


class UsersCreateFormTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_create_post(self):
        """ Валидная форма создает нового пользователя."""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Admin',
            'last_name': 'Admin1',
            'username': 'admin2',
            'email': 'admin@mail.com',
            'password1': 'PAS123456789',
            'password2': 'PAS123456789',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), users_count + 1)
