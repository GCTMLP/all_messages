import json
import logging
import threading
import time

from all_messages.api_controller.controller import ApiControllerForever
from all_messages.contacts.models import Messangers
from asgiref.sync import async_to_sync
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.db.utils import IntegrityError
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, TemplateView, View
from telethon import TelegramClient

from . import forms
from .models import ApiConnections, Profile

logger = logging.getLogger(__name__)


class Register(CreateView):
    """
    Регистрация пользователя
    """
    form_class = forms.NewUserForm
    template_name = 'register.html'
    success_url = "/"

    def form_valid(self, form):
        res = super().form_valid(form)
        user = form.save()
        if user:
            Profile.objects.create(user_id=user.id)
            login(self.request, user)
        return res


class SignUp(LoginView):
    """
    Вход пользователя
    """
    form_class = forms.LoginForm
    template_name = 'login.html'
    success_url = "/"

    def form_valid(self, form):
        res = super().form_valid(form)
        user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])
        if user is not None:
            print(self.request)
            login(self.request, user)
        return res


class MainPage(LoginRequiredMixin, TemplateView):
    """
    'Отрисовка' стартовой страницы (без данных), с прогруженными js
    """
    template_name = "start_page.html"
    redirect_field_name = '/login/'


class SettingsView(LoginRequiredMixin, TemplateView):
    """
    'Отрисовка' страницы настроек (без данных), с прогруженными js
    """
    template_name = "settings.html"


class AllSettingsView(View):
    """
    Получение всех данных пользователя + данных о подключенных API
    """
    def post(self, request):
        try:
            session_user = request.user.id
            user_settings_data = Profile.objects.get(user_id=session_user)
            user_data = {
                'user_name': user_settings_data.user.username,
                'email': user_settings_data.user.email,
                'name': user_settings_data.user.first_name,
                'surname': user_settings_data.user.last_name,
                'location': user_settings_data.location,
            }
            tg_s = ApiConnections.objects\
                .filter(Q(user_id=session_user)
                        & Q(messenger__messanger_name='telegram'))
            if tg_s.exists():
                tg_settings = {
                    'token': tg_s[0].token,
                    'app_id': tg_s[0].app_id,
                    'phone': tg_s[0].phone
                }
            else:
                tg_settings = []
            return_data = {}
            return_data['tg_settings'] = tg_settings
            return_data['user_data'] = user_data
            return JsonResponse(json.dumps(return_data), safe=False)
        except Exception as err:
            logger.error("Error in 'AllSettingsView': " + str(err))
            return JsonResponse('false', safe=False)


class ChangeSettingsView(View):
    """
    Изменение данных о пользователе
    """
    def post(self, request):
        try:
            session_user = request.user.id
            data_req = json.loads(request.body)
            user = User.objects.get(id=session_user)
            user.username = data_req['username']
            user.email = data_req['email']
            user.first_name = data_req['f_name']
            user.last_name = data_req['s_name']
            user.save()
            profile = Profile.objects.get(user_id=session_user)
            profile.location = data_req['location']
            profile.save()
            return JsonResponse('true', safe=False)
        except Exception as err:
            logger.error("Error in 'ChangeSettingsView': " + str(err))
            return JsonResponse('false', safe=False)


@method_decorator(csrf_exempt, name='dispatch')
class UserSession(View):
    """
    Класс обработки ajax запроса. Получаем информацию о пользователе
    от имени которого создалась сессия (для отображения инфорамции
    о пользователе в шапке)
    """
    def post(self, request):
        try:
            all_data = {}
            if request.user.is_authenticated:
                session_user = request.user.username
                qs = User.objects.get(username=session_user)
                all_data['username'] = session_user
                all_data['email'] = qs.email
            return JsonResponse(json.dumps(all_data), safe=False)
        except Exception as err:
            logger.error("Error in 'UserSession': " + str(err))
            return JsonResponse('false', safe=False)


class WriteTgCode(View):
    """
    Обработка телеграм кодов (предназначенных для создания сессии)
    которые пользователь ввел через веб-морду
    """
    def post(self, request):
        session_user = request.user.id
        request = json.loads(request.body)
        code_n = request['tr']
        token = request['token']
        tg_code = request['tg_code']
        user = User.objects.get(id=session_user)
        # записываем в базу данных введенные коды
        saved_api = ApiConnections.objects.get(token=token, user=user)
        if int(code_n) == 1:
            saved_api.code1 = tg_code
            saved_api.save()
        else:
            saved_api.code2 = tg_code
            saved_api.save()
        return JsonResponse('true', safe=False)


class RegisterApi(View):
    """
    Класс регистрации аккаунтов работы с API
    """
    @async_to_sync
    async def post(self, request):
        session_user = request.user.id
        request = json.loads(request.body)
        self.phone = request['phone']
        self.app_id = request['app_id']
        self.token = request['token']
        self.code = None
        if request['messenger'] == 'telegram':
            user = User.objects.get(id=session_user)
            messenger = Messangers.objects.get(messanger_name='telegram')
            save_api_sett = ApiConnections(token=self.token,
                                           app_id=self.app_id,
                                           phone=self.phone,
                                           messenger=messenger, user=user)
            try:
                save_api_sett.save()
            except IntegrityError:
                pass
            task = await self.connect_telegram()
            # В отдельном потоке запускаем мониторинг входящих сообщений
            t1 = MessageMonitor('telegram', session_user, self.phone,
                                self.app_id, self.token)
            t1.start()
            if task:
                return JsonResponse('true', safe=False)
            else:
                ApiConnections.objects.get(code=self.code).delete()
                return JsonResponse('false', safe=False)

    async def get_code(self, num):
        """
        Метод получения кода от телеграмма из бд, который ввел пользователь
        через веб-морду
        """
        code = None
        # получение кода для создания первой сессии
        if int(num) == 1:
            while not code:
                print(1)
                code = (ApiConnections.objects.get(token=self.token)).code1
                time.sleep(5)
        # получение кода для создания второй сессии
        if int(num) == 2:
            while not code:
                print(2)
                code = (ApiConnections.objects.get(token=self.token)).code2
                time.sleep(5)
        return code

    async def connect_telegram(self):
        """
        Метод создания 2ух сесиий (1 для мониторинга входящих сообщений,
        другая для отправки)
        """
        try:
            client = TelegramClient('tg_sessions/'+self.phone+'_'+self.app_id,
                                    self.app_id, self.token)
            await client.connect()
            if not await client.is_user_authorized():
                await client.send_code_request(self.phone)
                await client.sign_in(self.phone, await self.get_code(1))
                await client.disconnect()
                client1 = TelegramClient('tg_sessions/' + self.phone + '_'
                                         + self.app_id + 'get_mess',
                                         self.app_id, self.token)
                await client1.connect()
                await client1.send_code_request(self.phone)
                await client1.sign_in(self.phone, await self.get_code(2))
                await client1.disconnect()
            return True
        except Exception as err:
            logger.error("Can`t create telegram sessions: " + str(err))


class MessageMonitor(threading.Thread):
    """
    Создание трэда, в котором инициализируем подключение к апи телеграмма
    и мониторим входящие сообщения
    """
    def __init__(self, messenger, user_id, phone=None, tg_app_id=None,
                 tg_token=None):
        threading.Thread.__init__(self)
        self.messenger = messenger
        self.phone = phone
        self.app_id = tg_app_id
        self.token = tg_token
        self.user_id = user_id

    def run(self, *args, **kwargs):
        print(self.phone)
        ApiControllerForever(self.messenger, self.user_id, self.phone,
                             self.app_id, self.token)
