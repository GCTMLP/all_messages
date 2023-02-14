from django.urls import path

from .views import ChatsView

# URL, отвечающие за отображение окна чата
urlpatterns = [
    path('', ChatsView.as_view(), name='chats'),
]
