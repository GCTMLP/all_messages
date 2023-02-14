from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.user = User.objects.create_user(username='lipa')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_settings_template(self):
        response = self.authorized_client.get(reverse('settings'))
        self.assertTemplateUsed(response, 'settings.html')

    def test_chats_template(self):
        response = self.authorized_client.get(reverse('chats'))
        self.assertTemplateUsed(response, 'chats.html')

    def test_contacts_template(self):
        response = self.authorized_client.get(reverse('contacts'))
        self.assertTemplateUsed(response, 'contacts.html')
