from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UserPagesTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='auth')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон в приложении users."""
        temlates_pages_name = {
            'users/signup.html': reverse('users:signup'),
            'users/login.html': reverse('users:login'),
            'users/password_reset_form.html': (
                reverse('users:password_reset_form')
            ),
            'users/password_reset_done.html': (
                reverse('users:password_reset_done')
            ),
            'users/password_reset_complete.html': (
                reverse('users:password_reset_complete')
            ),
            'users/password_reset_confirm.html': (
                reverse(
                    'password_reset_confirm', kwargs={
                        'uidb64': 'NA', 'token': '5xb-40c48394b7a17cd5764e'
                    }
                )
            ),
            'users/password_change_form.html': (
                reverse('users:password_change_form')
            ),
            'users/password_change_done.html': (
                reverse('users:password_change_done')
            ),
            'users/logged_out.html': reverse('users:logout'),
        }
        for template, reverse_name in temlates_pages_name.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
