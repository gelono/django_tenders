from threading import Thread

from tenders.parsing.parsing import manager_for_collecting_links, manager_for_processing_active_tenders


def start_parse_prozorro():
    p1 = Thread(target=manager_for_collecting_links, args=(5, ))
    p2 = Thread(target=manager_for_processing_active_tenders, args=(5,))

    p1.start()
    p2.start()
