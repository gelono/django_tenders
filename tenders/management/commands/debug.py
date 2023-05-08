from django.core.management import BaseCommand

# from django_tenders.google_sheets import write_from_google_sheets
# from tenders.models import ArchiveTender, Customer, Winner, DKNumber, ActiveTender, Subscriber
# from tenders.parsing.parse import start_parse_prozorro
# from tenders.parsing.parsing import manager_for_processing_active_tenders
# from tenders.parsing.tools import get_api_data_for_db, django_orm_insert_into_arch_act, check_match


class Command(BaseCommand):
    def handle(self, *args, **options):
        # start_parse_prozorro()

        # tenders = ActiveTender.objects.all()[:50]
        # write_from_google_sheets(tenders)
        pass