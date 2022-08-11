from django.test import TestCase, Client


class ViewTestClass(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = Client()

    def test_error_page(self):
        """
        При запросе несуществующей страницы возвращается:
        1) ошибка 404.
        2) кастомный шаблон по адресу core/404.html.
        """
        response = ViewTestClass.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'core/404.html')
