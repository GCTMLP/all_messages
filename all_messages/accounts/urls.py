from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import (AllSettingsView, ChangeSettingsView, MainPage, Register,
                    RegisterApi, SettingsView, SignUp, UserSession,
                    WriteTgCode)

# Набор URL, отвечающих за вход, выход и регистрацию в app accounts, а также
# настройки личного кабинета и подключения к API
urlpatterns = [
    path('login/', SignUp.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path("register/", Register.as_view(), name="register"),
    path("settings/", SettingsView.as_view(), name="settings"),
    path("settings/get_settings/", AllSettingsView.as_view(),
         name="all_settings"),
    path("settings/change_user_data/", ChangeSettingsView.as_view(),
         name="change_settings"),
    path('get_user_session_data/', UserSession.as_view(), name='user_session'),
    path("settings/register_api/", RegisterApi.as_view(), name="register_api"),
    path("settings/write_tg_code/", WriteTgCode.as_view(),
         name="register_api"),
    path("", MainPage.as_view(), name="profile"),
]
