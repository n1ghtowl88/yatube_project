from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='test_user',
        )
        cls.group = Group.objects.create(
            title='Группа для теста',
            slug='group-for-test',
            description='Группа нужна для проведения тестирования'
        )
        cls.post = Post.objects.create(
            text='Тестовая запись для проверки',
            author=cls.user,
            group=cls.group
        )

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verbose = {
            'text': 'Содержание записи',
            'group': 'Название группы',
            'author': 'Автор',
        }
        for value, expected in field_verbose.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_text = {
            'text': 'Напишите что-нибудь интересное',
            'group': 'Введите название группы',
        }
        for value, expected in field_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_post_object_name_is_combination_of_fields(self):
        """В поле __str__  объекта post записано значение словосочетание из поле
        post.author.username, post.group и post.text[:15]."""
        post = PostModelTest.post
        expected_post_object_name = (f'{post.author.username}, {post.group} - '
                                     f'{post.text[:15]}')
        self.assertEqual(expected_post_object_name, str(post))

    def test_group_object_name_is_title_field(self):
        """В поле __str__  объекта group записано значение поля group.title."""
        group = PostModelTest.group
        expected_group_object_name = group.title
        self.assertEqual(expected_group_object_name, str(group))
