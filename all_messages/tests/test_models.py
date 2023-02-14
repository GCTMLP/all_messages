from django.test import TestCase
from all_messages.contacts.models import AccountsContacts, Contacts, \
    PhoneNumbers, Messangers
from all_messages.accounts.models import ApiConnections


class TaskModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.contact = Contacts.objects.create(
            name='some_name',
            comment='some_comment',
            tg_id='367432647'
        )

        cls.phone = PhoneNumbers.objects.create(
            phone_number='89161341107'
        )

        cls.messenger = Messangers.objects.create(
            messanger_name='telegram'
        )

        cls.api_conn = ApiConnections.objects.create(
            messenger=cls.messenger,
            token='823947wjfhwef',
            app_id='123',
            phone='89161341107',
            code1='45634',
            code2='45634'
        )

    def test_conact_name_label(self):
        task = TaskModelTest.contact
        verbose = task._meta.get_field('name').verbose_name
        self.assertEqual(verbose, 'name')

    def test_conact_comment_label(self):
        task = TaskModelTest.contact
        verbose = task._meta.get_field('comment').verbose_name
        self.assertEqual(verbose, 'comment')

    def test_conact_tg_id_label(self):
        task = TaskModelTest.contact
        verbose = task._meta.get_field('tg_id').verbose_name
        self.assertEqual(verbose, 'tg id')

    def test_conact_name_lengt(self):
        task = TaskModelTest.contact
        verbose = task._meta.get_field('name').max_length
        self.assertEqual(verbose, 100)

    def test_conact_comment_lengt(self):
        task = TaskModelTest.contact
        verbose = task._meta.get_field('comment').max_length
        self.assertEqual(verbose, 5000)

    def test_conact_tg_id_lengt(self):
        task = TaskModelTest.contact
        verbose = task._meta.get_field('tg_id').max_length
        self.assertEqual(verbose, 30)

    def test_conact_name_data(self):
        task = TaskModelTest.contact
        data = task.name
        self.assertEqual(data, 'some_name')

    def test_phone_phone_number_label(self):
        task = TaskModelTest.phone
        verbose = task._meta.get_field('phone_number').verbose_name
        self.assertEqual(verbose, 'phone number')

    def test_phone_phone_number_length(self):
        task = TaskModelTest.phone
        verbose = task._meta.get_field('phone_number').max_length
        self.assertEqual(verbose, 100)

    def test_phone_phone_number_data(self):
        task = TaskModelTest.phone
        data = task.phone_number
        self.assertEqual(data, '89161341107')

    def test_messenger_messenger_name_label(self):
        task = TaskModelTest.messenger
        verbose = task._meta.get_field('messanger_name').verbose_name
        self.assertEqual(verbose, 'messanger name')

    def test_messenger_messenger_name_length(self):
        task = TaskModelTest.messenger
        verbose = task._meta.get_field('messanger_name').max_length
        self.assertEqual(verbose, 100)

    def test_messenger_messenger_name_data(self):
        task = TaskModelTest.messenger
        data = task.messanger_name
        self.assertEqual(data, 'telegram')

    def test_api_token_length(self):
        task = TaskModelTest.api_conn
        verbose = task._meta.get_field('token').max_length
        self.assertEqual(verbose, 100)

    def test_api_token_data(self):
        task = TaskModelTest.api_conn
        data = task.token
        self.assertEqual(data, '823947wjfhwef')
