from django.urls import path, re_path

from . import consumer

# URL для веб-сокетов
websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<id>.+)', consumer.ChatConsumer.as_asgi()),
    path(r'ws/chat/left_chat', consumer.ChatConsumer.as_asgi())
]
