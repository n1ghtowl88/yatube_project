import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms

from ..models import Comment, Group, Post, User


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
SLUG = 'group-for-test'
AUTHOR_USERNAME = 'test_author'
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
GIF_NAME = 'small.gif'
GIF_NAME_2 = 'small_2.gif'
INDEX_URL = reverse('posts:index')
NEW_POST_URL = reverse('posts:post_create')
PROFILE_URL = reverse('posts:profile', args=[AUTHOR_USERNAME])


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username=AUTHOR_USERNAME,
        )
        cls.group = Group.objects.create(
            title='Группа для теста',
            slug=SLUG,
        )
        cls.UPLOADED = SimpleUploadedFile(
            name=GIF_NAME,
            content=SMALL_GIF,
            content_type='image/gif'
        )
        cls.UPLOADED_2 = SimpleUploadedFile(
            name=GIF_NAME_2,
            content=SMALL_GIF,
            content_type='image/gif'
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def setUp(self):
        self.post = Post.objects.create(
            text='Тестовый пост',
            author=PostFormTests.user,
        )
        self.POST_URL = reverse(
            'posts:post_detail',
            args=[self.post.id])
        self.POST_EDIT_URL = reverse(
            'posts:post_edit',
            args=[self.post.id])
        self.POST_COMMENT_URL = reverse(
            'posts:add_comment',
            args=[self.post.id])

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_create_post(self):
        """Валидная форма создает объект класса Post"""
        Post.objects.all().delete()
        posts_count = 0
        form_data = {
            'group': PostFormTests.group.id,
            'text': 'Тестовая запись для нового поста',
            'image': self.UPLOADED,
        }
        response = PostFormTests.authorized_client.post(
            NEW_POST_URL,
            data=form_data,
            follow=True,
        )
        posts_set = response.context['page_post_list']
        self.assertRedirects(response, PROFILE_URL)
        self.assertEqual(len(posts_set), posts_count + 1)
        self.assertEqual(posts_set[0].text, form_data['text'])
        self.assertEqual(posts_set[0].author, PostFormTests.user)
        self.assertEqual(posts_set[0].group, PostFormTests.group)
        self.assertNotEqual(posts_set[0].image, None)

    def test_edit_post(self):
        """Валидная форма изменяет объект класса Post"""
        form_data = {
            'group': PostFormTests.group.id,
            'text': 'Измененная тестовая запись',
            'image': self.UPLOADED_2,
        }
        response = PostFormTests.authorized_client.post(
            self.POST_EDIT_URL,
            data=form_data,
            follow=True,
        )
        post_update = response.context['post']
        self.assertRedirects(response, self.POST_URL)
        self.assertEqual(post_update.text, form_data['text'])
        self.assertEqual(post_update.author, PostFormTests.user)
        self.assertEqual(post_update.group, PostFormTests.group)
        self.assertNotEqual(post_update.image, None)

    def test_new_post_page_show_correct_context(self):
        """Шаблон страницы создания нового поста сформирован
        с правильным контекстом"""
        new_post_page_form_fields = {  # классы полей формы для поста
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        response = PostFormTests.authorized_client.get(NEW_POST_URL)
        for value, expected in new_post_page_form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_comment(self):
        """Валидная форма создает объект класса Comment"""
        Comment.objects.all().delete()
        comments_count = 0
        form_data = {
            'text': 'Тестовый комментарий',
        }
        response = PostFormTests.authorized_client.post(
            self.POST_COMMENT_URL,
            data=form_data,
            follow=True,
        )
        comments = response.context['comments']
        self.assertRedirects(response, self.POST_URL)
        self.assertEqual(len(comments), comments_count + 1)
        self.assertEqual(comments[0].text, form_data['text'])
        self.assertEqual(comments[0].author, PostFormTests.user)
        self.assertEqual(comments[0].post, self.post)

    def test_add_comment_page_show_correct_context(self):
        """Шаблон нового коммента на странице поста сформирован
        с правильным контекстом"""
        add_comment_form_fields = {  # классы полей формы для коммента
            'text': forms.fields.CharField,
        }
        response = PostFormTests.authorized_client.get(self.POST_URL)
        for value, expected in add_comment_form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_guest_cant_change_DB_when_trying_create_post(self):
        """Неавторизованный пользователь не изменит БД при
        попытках создать пост"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовая запись для попытки создания гостем',
        }
        PostFormTests.guest_client.post(
            NEW_POST_URL,
            data=form_data,
            follow=True,
        )
        self.assertEqual(Post.objects.count(), posts_count)

    def test_guest_cant_change_DB_when_trying_update_post(self):
        """Неавторизованный пользователь не изменит БД при
        попытках изменить пост"""
        form_data = {
            'group': PostFormTests.group.id,
            'text': 'Тестовая запись для попытки изменения гостем',
        }
        self.guest_client.post(
            self.POST_EDIT_URL,
            data=form_data,
            follow=True,
        )
        self.assertEqual(self.post, Post.objects.get(id=self.post.id))
