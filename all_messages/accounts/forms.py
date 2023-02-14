from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class NewUserForm(UserCreationForm):
    """
    Класс отрисовки формы регистрации
    """
    email = forms.EmailField(required=True)

    # Указываем модель и поля модели для отрисовки формы
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    # Метод сохранения данных в бд
    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    """
    Класс отрисовки формы входа
    """
    class Meta:
        model = User
        fields = ("username", "password")
