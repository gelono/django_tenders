import random

from django.core.management import BaseCommand
from faker import Faker

from tenders.models import Customer

fake = Faker(locale='en')


class Command(BaseCommand):
    def handle(self, *args, **options):
        ids = list(Customer.objects.values('id'))
        ids = [elem['id'] for elem in ids]
        domen = ['gmail.co', 'yahu.com', 'ucr.net', 'hotlin.com', 'list.ua']
        for i in ids:
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f'{first_name}_{last_name}@{random.choice(domen)}'
            Customer.objects.filter(id=i).update(customer_contact=email)