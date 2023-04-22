import random

from django.core.management import BaseCommand

from tenders.models import Customer, ArchiveTender


class Command(BaseCommand):
    def handle(self, *args, **options):
        id_tenders = list(ArchiveTender.objects.values('id'))
        id_tenders = [elem['id'] for elem in id_tenders]

        id_customers = list(Customer.objects.values('id'))
        id_customers = [elem['id'] for elem in id_customers]

        for i in id_tenders:
            ArchiveTender.objects.filter(id=i).update(customer_id=random.choice(id_customers))