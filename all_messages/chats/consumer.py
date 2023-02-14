import json
import logging
from datetime import datetime

from all_messages.accounts.models import ApiConnections
from all_messages.api_controller.controller import ApiController
from all_messages.contacts.models import AccountsContacts
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.sessions.models import Session
from django.db.models import Q

from .models import Messages

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Класс обработки веб-сокетов
    """
    http_user = True
    slight_ordering = True
    strict_ordering = False

    async def connect(self):
        """
        Подключение вебсокета
        """
        self.id = self.scope["url_route"]["kwargs"]["id"]
        self.sess_id = await self.get_session()
        self.room_group_name = "chat_{}_{}".format(self.id, self.sess_id)
        # Подключаемся к API мессенджеров для отправки сообщений
        await self.connect_to_messengers_api()
        # Если запрашиваем чат с контактом, проверяем принадлежит ли он
        # этому юзеру
        if self.id != 'left_chat':
            user_check = await self.check_session_id()
            # Если все ок, то добавляем подключение в layer
            # для таких же сокетов
            if user_check == int(self.sess_id):
                await self.channel_layer.group_add(self.room_group_name,
                                                   self.channel_name)
                await self.accept()
                data = await self.get_messages_data()
                await self.send(text_data=data)
        # Если необходимо отобразить список чатов (слева)
        else:
            await self.channel_layer.group_add(self.room_group_name,
                                               self.channel_name)
            await self.accept()
            data = await self.get_chats_data()
            await self.send(text_data=data)

    async def chat_message(self, event):
        """
        Метод получения event стороннего для сигнализации того, что пришло
        новое сообщение
        (для отображения значка new и для отрисовки сообщения в чате)
        """
        if event['left']:
            data = await self.get_chats_data(cont_id=event['contact'])
        else:
            data = await self.get_messages_data()
        await self.send(text_data=data)

    async def connect_to_messengers_api(self):
        """
        Метод подключения к API мессенджеров, создаем атрибут - коннектор
        """
        api_user_data = ApiConnections.objects.get(user_id=self.sess_id)
        self.connector = ApiController(self.sess_id, api_user_data.phone,
                                       api_user_data.app_id,
                                       api_user_data.token)

    @database_sync_to_async
    def get_session(self):
        """
        Метод получения текущей сессии пользователя
        """
        s = Session.objects.get(pk=self.scope['cookies']['sessionid'])
        sess_id = (s.get_decoded()['_auth_user_id'])
        return sess_id

    @database_sync_to_async
    def get_chats_data(self, cont_id=None):
        """
        Метод получения контактов с которыми можно вести чат
        """
        try:
            all_messages_from_db = Messages.objects\
                .filter(user_id=self.sess_id).values('ac_cont__contact__name',
                                                     'time',
                                                     'ac_cont__contact__id')
            all_chats = {}
            # Данные по ключу new необходимы для
            for chat in all_messages_from_db:
                all_chats[chat['ac_cont__contact__name'].strip()] = {}
                all_chats[chat['ac_cont__contact__name'].strip()]['new'] = 0
                if cont_id == chat['ac_cont__contact__id']:
                    all_chats[chat['ac_cont__contact__name'].strip()]['new']\
                        = 1
                all_chats[chat['ac_cont__contact__name'].strip()]['time'] = \
                    chat['time'].strftime("%d/%m/%Y %H:%m")
                all_chats[chat['ac_cont__contact__name'].strip()]['id'] = \
                    chat['ac_cont__contact__id']
            return json.dumps(all_chats)
        except Exception as err:
            logger.error("Error in 'ChatConsumer.get_chats_data': " + str(err))

    @database_sync_to_async
    def check_session_id(self):
        """
        Метод проверки принадлежности контакта пользователю, запрашиваемому
         чат с ним
        """
        try:
            user_id_contact = \
                AccountsContacts.objects.filter(contact__id=self.id)[0]
            return user_id_contact.user_id
        except Exception as err:
            logger.error("Error in 'ChatConsumer.check_session_id': " +
                         str(err))

    @database_sync_to_async
    def get_messages_data(self):
        """
        Метод получения сообщений с конкретным контактом
        """
        try:
            all_messages_from_db = Messages.objects\
                .filter(ac_cont__contact__id=self.id)
            all_messages = []
            for message in all_messages_from_db:
                one_message = {}
                one_message['time'] = message.time.strftime("%d/%m/%Y %H:%m")
                one_message['in_out'] = message.inp_out
                one_message['message'] = message.message
                one_message['messenger'] = message.ac_cont\
                    .messanger.messanger_name
                all_messages.append(one_message)
                name = message.ac_cont.contact.name
                comment = message.ac_cont.contact.comment
            all_data = {'messages': all_messages, 'name': name,
                        'comment': comment}
            return json.dumps(all_data)
        except Exception as err:
            logger.error("Error in 'ChatConsumer.get_messages_data': " +
                         str(err))

    async def disconnect(self, close_code):
        """
        Метод отключения веб-сокета
        """
        logger.info(f"Websocket {self.id} in "
                    f"{self.room_group_name} disconnected")
        await self.channel_layer.group_discard(self.room_group_name,
                                               self.channel_name)
        await self.close()

    async def receive(self, text_data):
        """
        Метод получения сообщений от веб-сокета
        """
        text_data_json = json.loads(text_data)
        try:
            # Пробегаемся по мессенджерам для отправки
            for messenger in text_data_json['mess']:
                # Подключение в API месседжера и отправка сообщения
                await self.connector.connect(messenger)
                success = await self.connector.send(messenger,
                                                    text_data_json['text'],
                                                    self.id)
                # Если сообщение отправлено - записываем в бд и отправляем
                # данные в сокет
                if success:
                    try:
                        current_datetime = datetime.now()
                        acc_id = AccountsContacts.objects\
                            .filter(Q(contact_id=self.id) &
                                    Q(messanger_id__messanger_name=messenger))
                        save_message = Messages(message=text_data_json['text'],
                                                time=current_datetime,
                                                inp_out=0,
                                                ac_cont_id=acc_id[0].id,
                                                user_id=self.sess_id)
                        save_message.save()
                        data = await self.get_messages_data()
                        await self.send(text_data=data)
                    except Exception as err:
                        logger.error("Error in writing message to db in "
                                     "'ChatConsumer.receive': " + str(err))
        except Exception as err:
            logger.error("Error in sending message from service to API: " +
                         str(err))
