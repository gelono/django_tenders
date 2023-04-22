from pprint import pprint
import pandas as pd
from django.core.management import BaseCommand

from tenders.models import ArchiveTender, DKNumber


class Command(BaseCommand):
    def handle(self, *args, **options):
        df = pd.read_excel('/home/oleg/Загрузки/from Serever109/tenders_archivetender.xlsx', header=0)
        ids = df.id.to_list()
        dks = df.dk_numbers.to_list()
        dks = [dk.split(', ') for dk in dks]
        query = []
        for i, dk in zip(ids, dks):
            query.append([i, dk])

        # query = list(ArchiveTender.objects.values('id', 'dk_numbers'))
        # query = [list(dct.values()) for dct in query]
        # query = [list((lst[0], lst[-1].split(', '))) for lst in query]
        #
        dk = list(DKNumber.objects.values('id', 'dk_number'))
        dk = [list(dct.values()) for dct in dk]
        dk_dct = {}
        for lst in dk:
            dk_dct[lst[0]] = lst[1]

        def get_key(dct, value):
            for k, v in dct.items():
                if v == value:
                    return k

        for t in query:
            for i in range(len(t[1])):
                t[1][i] = get_key(dk_dct, t[1][i])
        # pprint(query)

        for i in query:
            tender = ArchiveTender.objects.get(id=i[0])
            for j in i[-1]:
                if j:
                    tender.dk_numbers.add(
                        DKNumber.objects.get(id=j)
                    )

