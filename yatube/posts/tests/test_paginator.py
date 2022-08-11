from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User
from ..settings import ITEMS_PER_PAGE

SLUG = 'group-for-test'
TOTAL_NUMBER_OF_POSTS = ITEMS_PER_PAGE + 4
INDEX_PAGE_1_URL = reverse('posts:index')
INDEX_PAGE_2_URL = INDEX_PAGE_1_URL + '?page=2'
GROUP_PAGE_1_URL = reverse('posts:group_list', args=[SLUG])
GROUP_PAGE_2_URL = GROUP_PAGE_1_URL + '?page=2'


class PaginatorViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(
            username='test_user',
        )
        cls.group = Group.objects.create(
            title='Тест-группа',
            slug=SLUG,
            description='Группа для тестирования'
        )
        # First post without group
        Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
        )
        # Last 13 posts with group
        for index in range(2, TOTAL_NUMBER_OF_POSTS + 1):
            test_post = Post.objects.create(
                text='Тестовый пост',
                author=cls.user,
                group=cls.group
            )
            if index == 2:
                cls.post = test_post
        cls.guest_client = Client()

    def test_first_index_page_contains_correct_number_of_records(self):
        """1ая часть главной страницы содержит
        постов в количестве ITEMS_PER_PAGE"""
        response = PaginatorViewsTests.guest_client.get(INDEX_PAGE_1_URL)
        self.assertEqual(
            len(response.context['page_post_list']),
            ITEMS_PER_PAGE
        )

    def test_second__index_page_contains_correct_number_of_records(self):
        """2ая часть главной страницы содержит постов в количестве
        (TOTAL_NUMBER_OF_POSTS - ITEMS_PER_PAGE) штук"""
        response = PaginatorViewsTests.guest_client.get(INDEX_PAGE_2_URL)
        self.assertEqual(
            len(response.context['page_post_list']),
            TOTAL_NUMBER_OF_POSTS - ITEMS_PER_PAGE
        )

    def test_first_group_page_contains_correct_number_of_records(self):
        """1ая часть страницы группы содержит
        постов в количестве ITEMS_PER_PAGE"""
        response = PaginatorViewsTests.guest_client.get(GROUP_PAGE_1_URL)
        self.assertEqual(
            len(response.context['page_post_list']),
            ITEMS_PER_PAGE
        )

    def test_second_group_page_contains_correct_number_of_records(self):
        """2ая часть страницы группы содержит постов в количестве
        (TOTAL_NUMBER_OF_POSTS - ITEMS_PER_PAGE - 1) штук"""
        response = PaginatorViewsTests.guest_client.get(GROUP_PAGE_2_URL)
        self.assertEqual(len(
            response.context['page_post_list']),
            TOTAL_NUMBER_OF_POSTS - ITEMS_PER_PAGE - 1
        )
