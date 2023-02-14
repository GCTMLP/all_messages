import asyncio
import logging

from all_messages.accounts.models import ApiConnections
from all_messages.chats.models import Messages
from all_messages.contacts.models import (AccountsContacts, Contacts,
                                          PhoneNumbers)
from channels.layers import get_channel_layer
from config.settings import BASE_DIR
from django.db.models import Q
from telethon import TelegramClient, events, functions
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import InputPhoneContact

logger = logging.getLogger(__name__)


class ApiControllerForever:
    """
    Класс для подключения к API для мониторинга полученных сообщений
    """
    def __init__(self, messenger, user_id, phone=None, tg_app_id=None,
                 tg_token=None):
        self.messenger = messenger
        self.phone = phone
        self.app_id = tg_app_id
        self.token = tg_token
        self.user_id = user_id
        self.my_tg_id = user_id

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        if self.messenger == 'telegram':
            self.client = TelegramClient(BASE_DIR+'/tg_sessions/'
                                         + self.phone + '_' + self.app_id,
                                         self.app_id, self.token)

            # мониторинг полученных сообщений в телеграмм
            @self.client.on(events.NewMessage)
            async def handler_new_message(event):
                print(event.message.from_id.user_id)
                try:
                    await self.save_message(event)
                except Exception as e:
                    print(e)
            # запускаем клиента телеграм
            self.client.start()
            self.client.loop.run_forever()

    async def get_user(self, user_id):
        """
        Метод получения данных о пользователе, приславшем сообщение
        """
        user = await self.client(GetFullUserRequest(int(user_id)))
        return user

    async def save_message(self, event):
        """
        Метод сохранения нового сообщения в базу данных
        """
        user_id = event.message.from_id.user_id
        user_data = await self.get_user(user_id)
        my_phone = ApiConnections.objects.get(app_id=self.app_id)
        # чтобы не записывал исходящие сообщения как входящие
        if my_phone.phone[-10:] == user_data.user.phone[-10:]:
            return
        contact = Contacts.\
            objects.filter(accountscontacts__phone_id__phone_number=user_data
                           .user.phone)
        # Проверяем есть ли такой контакт в нашем сервисе ()
        if contact.exists():
            acc_id = AccountsContacts.objects.\
                filter(contact_id=contact[0].id,
                       messanger_id=1,
                       phone_id__phone_number=user_data.user.phone,
                       user_id=self.user_id)

            save_message = Messages(message=event.text,
                                    time=event.message.date,
                                    inp_out=1, ac_cont_id=acc_id[0].id,
                                    user_id=self.user_id)
        else:
            # Если контакта нет, то создаем его
            try:
                phone = user_data.user.phone
                username = user_data.user.username
            except Exception:
                phone = ''
                username = ''
            save_contact = Contacts(name='New contact', comment='new contact',
                                    tg_id=username)
            save_contact.save()
            save_phone = PhoneNumbers(phone_number=phone)
            save_phone.save()
            new_account = AccountsContacts(contact=save_contact,
                                           messanger_id=1,
                                           user_id=self.user_id,
                                           phone=save_phone)
            new_account.save()
            save_message = Messages(message=event.text,
                                    time=event.message.date,
                                    inp_out=1, ac_cont=new_account,
                                    user_id=self.user_id)
        save_message.save()
        # Отправка сигнала об ивенте (новое сообщение) в веб-сокет
        layer = get_channel_layer()
        # Для отображения в чатах в левой части экрана
        await layer.group_send(
            'chat_left_chat_'+str(self.user_id),
            {"type": "chat.message", "left": True, "text": event.text,
             "contact": contact[0].id},
        )
        # Для отображения в самом чате
        await layer.group_send(
            'chat_{}_{}'.format(str(contact[0].id), str(self.user_id)),
            {"type": "chat.message", "left": False, "text": event.text,
             "contact": contact[0].id},
        )


class ApiController:
    """
    Класс для разового подключения к API (для совершения короткого по времени
    действия, например, отправка сообщения)
    """
    def __init__(self, user_id, phone=None, tg_app_id=None, tg_token=None):
        self.phone = phone
        self.app_id = tg_app_id
        self.token = tg_token
        self.user_id = user_id

    async def connect(self, messenger):
        """
        Метод подключения к API
        """
        if messenger == 'telegram':
            self.client = TelegramClient(BASE_DIR+'/tg_sessions/' + self.phone
                                         + '_' + self.app_id+'get_mess',
                                         self.app_id, self.token)
            await self.client.start()

    async def send(self, messenger, text, contact_id):
        """
        Метод отправки сообщения
        """
        if messenger == 'telegram':
            acc_username = await self.get_id_by_phone_number(messenger,
                                                             contact_id)
            await self.client.send_message(acc_username, text)
        await self.client.disconnect()
        return True

    async def get_id_by_phone_number(self, messenger, contact_id):
        """
        Метод получения username пользователя телеграм по номеру телефона
        из базы данных
        """
        contact_data = AccountsContacts.objects.filter(
            Q(contact_id=contact_id) &
            Q(messanger_id__messanger_name=messenger)).values(
            'phone_id__phone_number', 'contact_id__id', 'contact_id__tg_id')[0]
        contact_id__tg_id = contact_data['contact_id__tg_id']
        # Смотрим, записан ли iusename в базу, еслм записан - возвращаем его,
        # если нет, то получаем его через get_user_id
        if not contact_id__tg_id:
            contact_id__tg_id = await self.get_user_id(
                contact_data['phone_id__phone_number'])
            cont = Contacts.objects.get(id=contact_data['contact_id__id'])
            cont.tg_id = contact_id__tg_id
            cont.save()
        return contact_id__tg_id

    async def get_user_id(self, phone):
        """
        Метод получения username пользователя телеграм по
        номеру телефона через добавление в контакты и через get_entity
        """
        contact = InputPhoneContact(client_id=0, phone=phone,
                                    first_name="custom_first_name",
                                    last_name="custom_last_name")
        await self.client(functions.contacts.ImportContactsRequest([contact]))
        contact_info = await self.client.get_entity(phone)
        return contact_info.username
