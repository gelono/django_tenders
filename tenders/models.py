from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


# Create your models here.
class ExtendedCompanyData(models.Model):
    fullname = models.CharField(max_length=500)
    shortname = models.CharField(max_length=500)
    location = models.CharField(max_length=1000)
    email = models.EmailField(null=True)
    primary_activity = models.CharField(max_length=500)
    ceo_name = models.CharField(max_length=500)
    capital = models.FloatField(null=True)

    def __str__(self):
        return self.shortname


class Customer(models.Model):
    name = models.CharField(max_length=500, unique=True)
    edrpou = models.CharField(max_length=100, unique=True)
    person_contact = models.EmailField(null=True)
    data = models.OneToOneField(ExtendedCompanyData, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name


class Winner(models.Model):
    name = models.CharField(max_length=500, unique=True)
    data = models.OneToOneField(ExtendedCompanyData, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name


class DKNumber(models.Model):
    dk = models.CharField(max_length=100)
    description = models.CharField(max_length=2000)

    def __str__(self):
        return self.dk


class ArchiveTender(models.Model):
    link = models.CharField(max_length=500, null=True)
    status = models.CharField(max_length=100, null=True)
    tender_name = models.CharField(max_length=10000, null=True)
    dk_numbers = models.ManyToManyField(DKNumber)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    initial_price = models.FloatField(null=True)
    finish_price = models.FloatField(null=True)
    winner = models.ForeignKey(Winner, on_delete=models.CASCADE, null=True)
    publication_date = models.DateField(null=True)
    inner_status = models.CharField(max_length=20, default='old')

    def __str__(self):
        return self.tender_name


class ActiveTender(models.Model):
    link = models.CharField(max_length=500, null=True)
    status = models.CharField(max_length=100, null=True)
    tender_name = models.CharField(max_length=10000, null=True)
    dk_numbers = models.ManyToManyField(DKNumber)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    initial_price = models.FloatField(null=True)
    finish_price = models.FloatField(null=True)
    winner = models.ForeignKey(Winner, on_delete=models.CASCADE, null=True)
    publication_date = models.DateField(null=True)
    inner_status = models.CharField(max_length=20, default='new')

    def __str__(self):
        return self.tender_name


class Subscriber(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    telegram_user_id = models.CharField(max_length=20, null=True)
    dk_numbers = models.ManyToManyField(DKNumber)

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('profile', kwargs={'username': self.user.username})


class SubscriberBalance(models.Model):
    subscriber = models.OneToOneField(Subscriber, on_delete=models.CASCADE)
    current_balance = models.FloatField(default=0.0)
    created = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    currency = models.CharField(max_length=10, default='UAH')

    def __str__(self):
        return str(self.current_balance)


class TransactionIn(models.Model):
    subscriber_balance = models.ForeignKey(SubscriberBalance, on_delete=models.CASCADE, null=True)
    created = models.DateTimeField(auto_now_add=True)
    amount = models.FloatField()
    currency = models.CharField(max_length=10)

    def __str__(self):
        return self.created


class TransactionOut(models.Model):
    subscriber_balance = models.ForeignKey(SubscriberBalance, on_delete=models.CASCADE, null=True)
    created = models.DateTimeField(auto_now_add=True)
    amount = models.FloatField()
    currency = models.CharField(max_length=10)

    def __str__(self):
        return self.created
