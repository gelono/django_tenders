from django.core.management import BaseCommand

from tenders.models import ArchiveTender, Customer, Winner, DKNumber, ActiveTender, Subscriber
from tenders.parsing.parse import start_parse_prozorro
from tenders.parsing.tools import get_api_data_for_db, django_orm_insert_into_arch_act, check_match


class Command(BaseCommand):
    def handle(self, *args, **options):
        start_parse_prozorro()
        # dct = get_api_data_for_db('08a8fdb1b61a467ea7ddb14de9e1e280', 0.3)
        # tenders = list(ActiveTender.objects.all().select_related('winner').values_list(
        #     'id', 'link', 'status', 'tender_name', 'customer_id', 'initial_price', 'finish_price',
        #     'winner__winner_name', 'publication_date', 'inner_status').order_by('id'))
        #
        # tender = list(tenders[0])
        # tender.pop(0)
        # tender.pop()
        # check_match(tender, dct)
        # instance = ActiveTender.objects.first()
        # dk_numbers = [dk.dk_number for dk in instance.dk_numbers.all()]
        # print(dk_numbers)

        # dict_for_database = get_api_data_for_db('e160d20e56e54604b017036b6f1b9a7f', 0.1)
        # dict_for_database['Номер тендеру'] = 'ДК021:2015:09130000-9'
        # django_orm_insert_into_arch_act(ActiveTender, dict_for_database)
