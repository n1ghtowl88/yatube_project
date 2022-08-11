from django.test import TestCase
from django.urls import reverse


UIDB64 = 'testuidb'
TOKEN = '123456'


class Tests(TestCase):
    """URLы, вычисляемые в маршрутах, соответствуют техническому заданию"""
    def test_correct_executed_urls(self):
        test_exec_url_expected_url = [
            [
                reverse('users:logout'),
                '/auth/logout/'
            ],
            [
                reverse('users:login'),
                '/auth/login/'
            ],
            [
                reverse('users:signup'),
                '/auth/signup/'
            ],
            [
                reverse('users:password_change'),
                '/auth/password_change/'
            ],
            [
                reverse('users:password_change_done'),
                '/auth/password_change/done/'
            ],
            [
                reverse('users:password_reset_form'),
                '/auth/password_reset/'
            ],
            [
                reverse('users:password_reset_done'),
                '/auth/password_reset/done/'
            ],
            [
                reverse('users:password_reset_confirm', args=[UIDB64, TOKEN]),
                f'/auth/reset/{UIDB64}/{TOKEN}/'
            ],
            [
                reverse('users:password_reset_complete'),
                '/auth/reset/done/'
            ],
        ]
        for exec_url, expected_url in test_exec_url_expected_url:
            self.assertEqual(exec_url, expected_url)
