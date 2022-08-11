from django.test import TestCase, Client
from django.urls import reverse

from ..models import Follow, Group, Post, User

SLUG = 'group-for-test'
USERNAME = 'test_user'
INDEX_URL = reverse('posts:index')
FOLLOW_URL = reverse('posts:follow_index')
GROUP_URL = reverse('posts:group_list', args=[SLUG])
NEW_POST_URL = reverse('posts:post_create')
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
FOLLOW_ACTION_URL = reverse('posts:profile_follow', args=[USERNAME])
UNFOLLOW_ACTION_URL = reverse('posts:profile_unfollow', args=[USERNAME])
LOGIN_URL = reverse('users:login')
LOGIN_URL_FROM_NEW_PAGE = f'{LOGIN_URL}?next={NEW_POST_URL}'
LOGIN_URL_FROM_FOLLOW_ACTION = f'{LOGIN_URL}?next={FOLLOW_ACTION_URL}'
LOGIN_URL_FROM_UNFOLLOW_ACTION = f'{LOGIN_URL}?next={UNFOLLOW_ACTION_URL}'
LOGIN_URL_FROM_FOLLOW_PAGE = f'{LOGIN_URL}?next={FOLLOW_URL}'
RANDOM_URL = '/random/'


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_user = User.objects.create(
            username=USERNAME,
        )
        cls.not_author_user = User.objects.create(
            username='test_not_author',
        )
        cls.group = Group.objects.create(
            title='Группа для теста',
            slug=SLUG,
            description='Группа нужна для проведения тестирования'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост №1',
            author=cls.author_user
        )
        cls.POST_URL = reverse('posts:post_detail', args=[
            cls.post.id])
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[
            cls.post.id])
        cls.guest_client = Client()
        cls.author_client = Client()
        cls.author_client.force_login(cls.author_user)
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author_user)

    def test_urls_exists_at_desired_location(self):
        """Проверяемые страницы выдают соответствующий код
         соответствующему пользователю."""
        test_url_client_status_code = [
            [INDEX_URL, PostURLTests.guest_client, 200],
            [GROUP_URL, PostURLTests.guest_client, 200],
            [NEW_POST_URL, PostURLTests.author_client, 200],
            [NEW_POST_URL, PostURLTests.guest_client, 302],
            [PROFILE_URL, PostURLTests.guest_client, 200],
            [PostURLTests.POST_URL, PostURLTests.guest_client, 200],
            [PostURLTests.POST_EDIT_URL, PostURLTests.author_client, 200],
            [PostURLTests.POST_EDIT_URL, PostURLTests.guest_client, 302],
            [PostURLTests.POST_EDIT_URL, PostURLTests.not_author_client, 302],
            [RANDOM_URL, PostURLTests.guest_client, 404],
            [FOLLOW_URL, PostURLTests.guest_client, 302],
            [FOLLOW_URL, PostURLTests.author_client, 200],
            [FOLLOW_ACTION_URL, PostURLTests.guest_client, 302],
            [FOLLOW_ACTION_URL, PostURLTests.author_client, 302],
            [UNFOLLOW_ACTION_URL, PostURLTests.guest_client, 302],
            [UNFOLLOW_ACTION_URL, PostURLTests.not_author_client, 302],
        ]
        Follow.objects.create(user=PostURLTests.not_author_user,
                              author=PostURLTests.author_user)
        for url, client, code in test_url_client_status_code:
            with self.subTest(url=url):
                self.assertEqual(client.get(url).status_code, code)

    def test_correct_redirects_for_various_users(self):
        """Проверяемые страницы/действия перенаправят соответствующего
        пользователя на соответствующую страницу."""
        guest = PostURLTests.guest_client
        not_author = PostURLTests.not_author_client
        test_url_client_redirect = [
            [NEW_POST_URL, guest, LOGIN_URL_FROM_NEW_PAGE],
            [PostURLTests.POST_EDIT_URL, guest, PostURLTests.POST_URL],
            [PostURLTests.POST_EDIT_URL, not_author, PostURLTests.POST_URL],
            [FOLLOW_ACTION_URL, guest, LOGIN_URL_FROM_FOLLOW_ACTION],
            [UNFOLLOW_ACTION_URL, guest, LOGIN_URL_FROM_UNFOLLOW_ACTION],
            [FOLLOW_URL, guest, LOGIN_URL_FROM_FOLLOW_PAGE],
            [FOLLOW_ACTION_URL, not_author, PROFILE_URL],
            [UNFOLLOW_ACTION_URL, not_author, PROFILE_URL],
        ]
        for url, client, redirect_url in test_url_client_redirect:
            with self.subTest(url=url):
                self.assertRedirects(client.get(url), redirect_url)

    def test_urls_uses_correct_template(self):
        """URL-адреса используют соответствующие шаблоны."""
        test_urls_templates = [
            [INDEX_URL, 'posts/index.html'],
            [FOLLOW_URL, 'posts/follow.html'],
            [GROUP_URL, 'posts/group_list.html'],
            [NEW_POST_URL, 'posts/create_post.html'],
            [PROFILE_URL, 'posts/profile.html'],
            [PostURLTests.POST_URL, 'posts/post_detail.html'],
            [PostURLTests.POST_EDIT_URL, 'posts/create_post.html'],

        ]
        for url, template in test_urls_templates:
            with self.subTest(url=url):
                self.assertTemplateUsed(
                    PostURLTests.author_client.get(url),
                    template
                )
