from django.test import TestCase
from django.urls import reverse


class Tests(TestCase):
    """URLы, вычисляемые в маршрутах, соответствуют техническому заданию"""
    def test_correct_executed_urls(self):
        test_exec_url_expected_url = [
            [
                reverse('about:about'),
                '/about/'
            ],
            [
                reverse('about:tech'),
                '/about/tech/'
            ],
        ]
        for exec_url, expected_url in test_exec_url_expected_url:
            self.assertEqual(exec_url, expected_url)
