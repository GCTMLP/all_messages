from django.db import models


class ApiConnections(models.Model):
    """
    Модель для хранения данных о подключениях к API сторонних сервисов
    """
    messenger = models.ForeignKey('contacts.Messangers',
                                  on_delete=models.CASCADE)
    token = models.CharField(max_length=100, null=True)
    app_id = models.CharField(max_length=15, null=True)
    phone = models.CharField(max_length=15)
    code1 = models.CharField(max_length=15, null=True)
    code2 = models.CharField(max_length=15, null=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=True)

    class Meta:
        unique_together = ('token', 'user')


class Profile(models.Model):
    """
    Модель, расширяющая модель Users (здесь добавятся поля еще)
    """
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    location = models.CharField(max_length=30, null=True)
