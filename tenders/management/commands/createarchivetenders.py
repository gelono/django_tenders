import random

import pandas as pd
from django.core.management import BaseCommand

from tenders.models import ArchiveTender, Customer, Winner


class Command(BaseCommand):
    def handle(self, *args, **options):
        df = pd.read_csv('/home/oleg/Загрузки/from Serever109/tenders_archivetender.csv', header=0)
        t_id = df.id.to_list()
        t_link = df.link.to_list()
        t_status = df.status.to_list()
        t_tender_name = df.tender_name.to_list()
        t_initial_price = df.initial_price.to_list()
        t_finish_price = df.finish_price.to_list()
        t_publication_date = df.publication_date.to_list()
        t_inner_status = df.inner_status.to_list()
        t_winner_old = df.winner_old.to_list()

        id_customers = list(Customer.objects.values('id'))
        id_customers = [elem['id'] for elem in id_customers]

        # winner_names = list(Winner.objects.values('winner_name'))
        # winner_names = [elem['winner_name'] for elem in winner_names]

        for i in range(4880):
            win_id = Winner.objects.get(winner_name=t_winner_old[i])
            ArchiveTender.objects.create(
                id=t_id[i],
                link=t_link[i],
                status=t_status[i],
                tender_name=t_tender_name[i],
                customer_id=random.choice(id_customers),
                initial_price=t_initial_price[i],
                finish_price=t_finish_price[i],
                publication_date=t_publication_date[i],
                inner_status=t_inner_status[i],
                winner_id=win_id.id
            )
