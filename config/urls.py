from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('all_messages.accounts.urls')),
    path('chats/', include('all_messages.chats.urls')),
    path('contacts/', include('all_messages.contacts.urls'))
]
