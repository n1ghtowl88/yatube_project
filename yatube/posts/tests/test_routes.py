from django.test import TestCase
from django.urls import reverse


SLUG = 'group-for-test'
USERNAME = 'test_user'
ID = 345


class Tests(TestCase):
    """URLы, вычисляемые в маршрутах, соответствуют техническому заданию"""
    def test_correct_executed_urls(self):
        test_exec_url_expected_url = [
            [
                reverse('posts:index'),
                '/'
            ],
            [
                reverse('posts:follow_index'),
                '/follow/'
            ],
            [
                reverse('posts:group_list', args=[SLUG]),
                f'/group/{SLUG}/'
            ],
            [
                reverse('posts:post_create'),
                '/create/'
            ],
            [
                reverse('posts:profile', args=[USERNAME]),
                f'/profile/{USERNAME}/'
            ],
            [
                reverse('posts:profile_follow', args=[USERNAME]),
                f'/profile/{USERNAME}/follow/'
            ],
            [
                reverse('posts:profile_unfollow', args=[USERNAME]),
                f'/profile/{USERNAME}/unfollow/'
            ],
            [
                reverse('posts:post_detail', args=[ID]),
                f'/posts/{ID}/'
            ],
            [
                reverse('posts:add_comment', args=[ID]),
                f'/posts/{ID}/comment/'
            ],
            [
                reverse('posts:post_edit', args=[ID]),
                f'/posts/{ID}/edit/'
            ],
        ]
        for exec_url, expected_url in test_exec_url_expected_url:
            self.assertEqual(exec_url, expected_url)
