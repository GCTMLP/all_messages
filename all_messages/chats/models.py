from django.db import models


class Messages(models.Model):
    """
    Модель описывающая сообщение
    связана с пользователем сервиса и контактом, с которым тот общается
    """
    message = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    ac_cont = models.ForeignKey('contacts.AccountsContacts',
                                on_delete=models.DO_NOTHING, null=True)
    inp_out = models.IntegerField()
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    class Meta:
        ordering = ('-time',)
