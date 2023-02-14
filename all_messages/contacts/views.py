import json
import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import JsonResponse
from django.views.generic import TemplateView, View

from .models import AccountsContacts, Contacts, PhoneNumbers

logger = logging.getLogger(__name__)


class ContactsView(LoginRequiredMixin, TemplateView):
    """
    'Отрисовка' базовой страницы (без данных), с прогруженными js
    """
    redirect_field_name = '/login/'
    template_name = "contacts.html"


class AllContactsView(View):
    """
    Получение данных о контактах пользователя
    """
    def post(self, request):
        session_user = request.user.id
        request = json.loads(request.body)
        page = int(request['page'])
        limit = int(request['limit'])
        search = request['search']
        # получение данных в зависимости от поискового запроса и страницы
        try:
            if search and search[0] != '#':
                contacts = AccountsContacts.objects.filter(
                    Q(user_id=int(session_user)) &
                    Q(contact__name__contains=search)).select_related(
                    'user', 'contact',
                    'messanger', 'phone')[(page-1)*limit:page*limit]
            else:
                contacts = AccountsContacts.objects.filter(
                    user_id=int(session_user)).select_related(
                    'user', 'contact',
                    'messanger', 'phone')[(page-1)*limit:page*limit]
            # формируем словарь данных о контактах
            return_data = {}
            all_contacts = {}
            for cont in contacts:
                one_contact = {}
                if cont.contact.id not in all_contacts.keys():
                    one_contact['comment'] = cont.contact.comment
                    one_contact['name'] = cont.contact.name
                    one_contact['contact'] = \
                        {cont.phone.phone_number.strip(): {'mess': [
                            cont.messanger.messanger_name], 'select': True}}
                    all_contacts[cont.contact.id] = one_contact
                elif cont.phone.phone_number.strip() in \
                        all_contacts[cont.contact.id]['contact'].keys():
                    all_contacts[cont.contact.id]['contact'][
                        cont.phone.phone_number.strip()]['mess'].append(
                        cont.messanger.messanger_name)
                else:
                    all_contacts[cont.contact.id]['contact'][
                        cont.phone.phone_number.strip()] = {
                        'mess': [cont.messanger.messanger_name],
                        'select': False}
            print(all_contacts)
            return_data['data'] = all_contacts
            return_data['count'] = AccountsContacts.objects\
                .filter(user_id=int(session_user))\
                .values('contact').annotate(c=Count('contact')).count()
            return_data = json.dumps(return_data)
            return JsonResponse(return_data, safe=False)
        except Exception as err:
            logger.error("Error in 'AllContactsView': "+str(err))


class ChangeContacts(View):
    """
    Редактируем контакт
    """
    def post(self, request):
        try:
            request = json.loads(request.body)
            id_contact = int(request['id'])
            name = request['name']
            comment = request['comment']
            Contacts.objects.filter(id=id_contact).update(name=name,
                                                          comment=comment)
            return JsonResponse('True', safe=False)
        except Exception as err:
            logger.error("Error in 'ChangeContacts': " + str(err))
            return JsonResponse('False', safe=False)


class DeleteContacts(View):
    """
    Удаляем контакт
    """
    def post(self, request):
        try:
            request = json.loads(request.body)
            id_contact = int(request['id'])
            Contacts.objects.filter(id=id_contact).delete()
            return JsonResponse('True', safe=False)
        except Exception as err:
            logger.error("Error in 'DeleteContacts': " + str(err))
            return JsonResponse('False', safe=False)


class AddContacts(View):
    """
    Изменяем контакт
    """
    def post(self, request):
        try:
            session_user = request.user.id
            request = json.loads(request.body)
            name = request['name']
            comment = request['comment']
            phones = request['phones'].split(';')
            save_contact = Contacts(name=name, comment=comment)
            save_contact.save()
            # если к одному контакту привязали несколько телефонов
            for phone in phones:
                save_phone = PhoneNumbers(phone_number=phone)
                save_phone.save()
                account_contact = AccountsContacts(phone=save_phone,
                                                   contact=save_contact,
                                                   user_id=session_user,
                                                   messanger_id=3)
                account_contact.save()
            return JsonResponse('True', safe=False)
        except Exception as err:
            logger.error("Error in 'AddContacts': " + str(err))
            return JsonResponse('False', safe=False)
