import pandas as pd
from django.core.management import BaseCommand

from tenders.models import Winner


class Command(BaseCommand):
    def handle(self, *args, **options):
        df = pd.read_csv('/home/oleg/Загрузки/from Serever109/tenders_archivetender.csv', header=0)
        check = []
        for n in df.winner_old:
            if n not in check:
                check.append(n)
                Winner.objects.create(winner_name=n)
