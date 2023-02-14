from django.urls import path

from .views import (AddContacts, AllContactsView, ChangeContacts, ContactsView,
                    DeleteContacts)

# Набор URL, отвечающих за страницу добавления и редактирования контактов
urlpatterns = [
    path('', ContactsView.as_view(), name='contacts'),
    path('get_all_contacts/', AllContactsView.as_view(), name='all_contacts'),
    path('change_contact_info/', ChangeContacts.as_view(), name='change'),
    path('delete_contact_info/', DeleteContacts.as_view(), name='delete'),
    path('add_contact_info/', AddContacts.as_view(), name='add')
]
