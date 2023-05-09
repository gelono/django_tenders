from django.core.management import BaseCommand

# from django_tenders.google_sheets import write_from_google_sheets
# from tenders.models import ArchiveTender, Customer, Winner, DKNumber, ActiveTender, Subscriber
# from tenders.parsing.parsing import manager_for_processing_active_tenders
# from tenders.parsing.tools import get_api_data_for_db, django_orm_insert_into_arch_act, check_match
# from tenders.parsing.parse import start_parse_prozorro
from tenders.parsing.tools import get_api_data_for_db


class Command(BaseCommand):
    def handle(self, *args, **options):
        # start_parse_prozorro()
        dct = get_api_data_for_db('2605149d816d414995eaeaefadbdd4a3', 0.3)
        print(dct)

