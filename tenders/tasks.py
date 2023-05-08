from celery import shared_task

from django_tenders.google_sheets import write_from_google_sheets
from tenders.models import Subscriber, ActiveTender
from tenders.parsing.telegram import send_telegram_message


@shared_task()
def user_notification(obj_id: int, link: str, message: str):
    text = message + link
    tender = ActiveTender.objects.get(id=obj_id)
    dk_numbers = [dk.dk_number for dk in tender.dk_numbers.all()]
    print(dk_numbers)
    for dk_number in dk_numbers:
        try:
            tg_user_ids = list(
                Subscriber.objects.values_list('telegram_user_id', flat=True).prefetch_related().
                filter(dk_numbers__dk_number=dk_number)
            )
        except Exception:
            print('[INFO] User emails are not received')
        else:
            if tg_user_ids:
                for tg_user_id in tg_user_ids:
                    send_telegram_message(tg_user_id, text)
                    print('Sending the message...')
            else:
                print('There are no users for notifications')


@shared_task()
def report_to_google_sheets():
    tenders = ActiveTender.objects.all()[:50]
    write_from_google_sheets(tenders)
