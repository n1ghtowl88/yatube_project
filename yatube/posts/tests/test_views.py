import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Follow, Group, Post, User


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
SLUG = 'group-with-post'
SLUG_EMPTY = 'group-without-post'
USERNAME = 'test_user'
AUTHOR_USERNAME = 'test_author'
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
INDEX_URL = reverse('posts:index')
FOLLOW_URL = reverse('posts:follow_index')
GROUP_WITH_POST_URL = reverse(
    'posts:group_list',
    args=[SLUG])
GROUP_WITHOUT_POST_URL = reverse(
    'posts:group_list',
    args=[SLUG_EMPTY])
NEW_POST_URL = reverse('posts:post_create')
PROFILE_URL = reverse('posts:profile',
                      args=[AUTHOR_USERNAME])
FOLLOW_ACTION_URL = reverse('posts:profile_follow',
                            args=[AUTHOR_USERNAME])
UNFOLLOW_ACTION_URL = reverse('posts:profile_unfollow',
                              args=[AUTHOR_USERNAME])


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author_user = User.objects.create(
            username=AUTHOR_USERNAME,
        )
        cls.user = User.objects.create(
            username=USERNAME,
        )
        cls.group_with_post = Group.objects.create(
            title='Группа для теста',
            slug=SLUG,
            description='Группа где будут посты'
        )
        cls.group_empty = Group.objects.create(
            title='Группа для теста 2',
            slug=SLUG_EMPTY,
            description='Группа без постов'
        )
        cls.UPLOADED = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост 1',
            author=cls.author_user,
            group=cls.group_with_post,
            image=cls.UPLOADED,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.author_user,
            text='Тестовый комментарий'
        )
        cls.POST_URL = reverse('posts:post_detail', args=[cls.post.id])
        cls.guest_client = Client()
        cls.author_client = Client()
        cls.author_client.force_login(cls.author_user)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_page_show_correct_context_for_post_objects(self):
        """Шаблон соответствующей страницы под соответствующим пользователем
        сформирован с правильным контекстом для объекта post"""
        test_url = [
            [INDEX_URL, PostPagesTests.author_client],
            [GROUP_WITH_POST_URL, PostPagesTests.author_client],
            [PROFILE_URL, PostPagesTests.author_client],
            [FOLLOW_URL, PostPagesTests.authorized_client],
        ]
        cache.clear()
        Follow.objects.create(
            user=PostPagesTests.user,
            author=PostPagesTests.author_user)
        for url, client in test_url:
            with self.subTest(url=url):
                posts = client.get(url).context['page_post_list']
                self.assertEqual(len(posts), 1)
                self.assertEqual(posts[0], PostPagesTests.post)

    def test_group_page_show_correct_context_for_group_object(self):
        """Шаблон страницы группы сформирован с правильным контекстом
        для объекта group"""
        self.assertEqual(
            PostPagesTests.author_client.get(GROUP_WITH_POST_URL).context[
                'group'],
            PostPagesTests.group_with_post
        )

    def test_page_show_correct_context_for_author_object(self):
        """Шаблон соответствующей страницы сформирован с правильным контекстом
        для объекта author"""
        self.assertEqual(
            PostPagesTests.author_client.get(PROFILE_URL).context['author'],
            PostPagesTests.author_user
        )

    def test_post_page_show_correct_context_for_post_object(self):
        """Шаблон страницы поста сформирован с правильным контекстом
        для объекта post"""
        response = PostPagesTests.author_client.get(PostPagesTests.POST_URL)
        self.assertEqual(
            response.context['post'],
            PostPagesTests.post
        )

    def test_post_page_show_correct_context_for_comment_object(self):
        """Шаблон страницы поста сформирован с правильным контекстом
        для объекта comment"""
        comments = PostPagesTests.author_client.get(
            PostPagesTests.POST_URL).context['comments']
        self.assertEqual(len(comments), 1)
        self.assertEqual(comments[0], PostPagesTests.comment)

    def test_post_with_group_not_in_other_group_page(self):
        """Пост с неуказанной группой не попадает на страницу с группой"""
        response = PostPagesTests.author_client.get(GROUP_WITHOUT_POST_URL)
        self.assertNotIn(
            PostPagesTests.post,
            response.context['page_post_list'])

    def test_author_post_not_in_follow_page_unfollow_user(self):
        """Пост автора не попадает на страницу подписок
         неподписанного пользователя"""
        Follow.objects.all().delete()
        cache.clear()
        response = PostPagesTests.authorized_client.get(FOLLOW_URL)
        self.assertNotIn(PostPagesTests.post, response.context[
            'page_post_list'])

    def test_index_page_test_save_page_context_correctly(self):
        """Кеширование контекста главной страницы корректно сохраняет
        контекст page"""
        cache.clear()
        content = PostPagesTests.author_client.get(INDEX_URL).content
        Post.objects.create(
            text='Тестовый пост 2',
            author=PostPagesTests.author_user,
            group=PostPagesTests.group_with_post,
        )
        cached_content = PostPagesTests.author_client.get(INDEX_URL).content
        self.assertEqual(content, cached_content)
        cache.clear()
        updated_content = PostPagesTests.author_client.get(INDEX_URL).content
        self.assertNotEqual(content, updated_content)

    def test_author_user_can_follow_to_other_user(self):
        """Авторизованный пользователь может подписываться
        на другого пользователя"""
        Follow.objects.all().delete()
        PostPagesTests.authorized_client.get(FOLLOW_ACTION_URL)
        self.assertEqual(
            Follow.objects.filter(
                user=PostPagesTests.user,
                author=PostPagesTests.author_user).exists(),
            True)

    def test_author_user_can_unfollow_to_other_user(self):
        """Авторизованный пользователь может отписываться
        от другого пользователя"""
        Follow.objects.create(
            user=PostPagesTests.user,
            author=PostPagesTests.author_user)
        PostPagesTests.authorized_client.get(UNFOLLOW_ACTION_URL)
        self.assertEqual(
            Follow.objects.filter(
                user=PostPagesTests.user,
                author=PostPagesTests.author_user).exists(),
            False)
