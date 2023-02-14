from django.db import models


class Contacts(models.Model):
    """
    Модель описывающая данные контакта
    """
    search_fields = ["name"]
    name = models.CharField(max_length=100)
    comment = models.CharField(max_length=5000)
    tg_id = models.CharField(max_length=30, null=True)

    class Meta:
        ordering = ('name',)


class PhoneNumbers(models.Model):
    """
    Модель всех номеров телефонов
    """
    phone_number = models.CharField(max_length=100)


class Messangers(models.Model):
    """
    Модель всех номеров мессенджеров и социальных сетей
    """
    messanger_name = models.CharField(max_length=100)


class AccountsContacts(models.Model):
    """
    Модель, связывающая контакт, его номера телефоном и мессенджеры, к которым
    привязан конкретный номер телефона. Некий список аккаунтов
    """
    messanger = models.ForeignKey('Messangers', on_delete=models.DO_NOTHING,
                                  null=True)
    phone = models.ForeignKey('PhoneNumbers', on_delete=models.DO_NOTHING,
                              null=True)
    contact = models.ForeignKey('Contacts', on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
