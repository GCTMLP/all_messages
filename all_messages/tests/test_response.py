from django.test import TestCase
from django.test import Client


class ViewsTestCase(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_login_loads_properly(self):
        response = self.client.get('http://127.0.0.1:8000/login/')
        self.assertEqual(response.status_code, 200)

    def test_register_loads_properly(self):
        response = self.client.get('http://127.0.0.1:8000/register/')
        self.assertEqual(response.status_code, 200)

    def test_login_to_service(self):
        c = Client()
        response = c.post('http://127.0.0.1:8000/login/',
                          {'username': 'lipa', 'password': '123'})

        self.assertEqual(response.status_code, 200)
