from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.core.exceptions import ValidationError

from tenders.models import Subscriber


class RegisterUserForm(UserCreationForm):
    first_name = forms.CharField(label="Ім'я", widget=forms.TextInput(attrs={'class': 'form-input'}))
    last_name = forms.CharField(label="Прізвище", widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-input'}))
    phone_number = forms.CharField(label='Телефон', widget=forms.TextInput(attrs={'class': 'form-input'}))
    username = forms.CharField(label='Логін', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'username', 'password1', 'password2')


class UpdateUserForm(forms.ModelForm):
    first_name = forms.CharField(label="Ім'я", widget=forms.TextInput(attrs={'class': 'form-input'}))
    last_name = forms.CharField(label="Прізвище", widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-input'}))
    phone_number = forms.CharField(label='Телефон', widget=forms.TextInput(attrs={'class': 'form-input'}))
    username = forms.CharField(label='Логін', widget=forms.TextInput(attrs={'class': 'form-input'}))
    telegram_user_id = forms.CharField(label="Telegram user id", widget=forms.TextInput(attrs={'class': 'form-input'}))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'username', 'telegram_user_id')

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if not phone_number[1:].isnumeric() or len(phone_number) > 15:
            raise ValidationError('Phone number must be a 15-digit numeric value or less')
        return phone_number

    def clean_telegram_user_id(self):
        telegram_user_id = self.cleaned_data['telegram_user_id']
        if len(telegram_user_id) > 20:
            raise ValidationError('Telegram user id must contain less than 21 symbols')
        return telegram_user_id

    def save(self, commit=True):
        user = super().save(commit=False)

        # Update Subscriber model fields
        subscriber, created = Subscriber.objects.get_or_create(user=user)
        subscriber.phone_number = self.cleaned_data['phone_number']
        subscriber.telegram_user_id = self.cleaned_data['telegram_user_id']
        subscriber.save()

        if commit:
            user.save()

        return user
