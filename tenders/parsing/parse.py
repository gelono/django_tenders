from threading import Thread

from celery import shared_task

from tenders.parsing.parsing import manager_for_collecting_links, manager_for_processing_active_tenders


@shared_task()
def start_parse_prozorro():
    p1 = Thread(target=manager_for_collecting_links, args=(5, ))
    p2 = Thread(target=manager_for_processing_active_tenders, args=(5,))

    p1.start()
    p2.start()


# start_parse_prozorro()
