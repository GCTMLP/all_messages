from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class ChatsView(LoginRequiredMixin, TemplateView):
    """
    'Отрисовка' базовой страницы (без данных), с прогруженными js
    """
    template_name = "chats.html"
    redirect_field_name = '/login/'
