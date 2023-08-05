import time
from datetime import datetime
import threading

import requests
from pytz import timezone
from tenders.models import ArchiveTender, ActiveTender

import urllib3

from tenders.parsing.tools import get_api_data_for_db, django_orm_insert_into_arch_act, check_match, \
    django_orm_update_arch_act

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def parse_with_tender_id_by_api(total_links, start, step, bot, sleep, is_archivating=False):
    """
    Parsing tenders by id (via API), separation into active and completed in the database
    :param sleep:
    :param bot: int - Stream sequence number
    :param total_links: list - list id
    :param start: int - start index reading list total_links
    :param step: int - total_links list reading step
    :param is_archivating: bool
    :return:
    """

    dict_for_database = {}
    count = 0
    start_index = start

    # ----------------------------------------
    for i in range(start_index, len(total_links), step):
        link = f'https://prozorro.gov.ua/tender/{total_links[i]}'
        count += 1

        try:
            dict_for_database = get_api_data_for_db(total_links[i], sleep)
        except Exception as e:
            print(f'[INFO from bot# {bot}] Data {total_links[i]} was not collected from the page', e, count, link)

        try:
            if is_archivating:
                if dict_for_database['Статус'] in ('complete', 'unsuccessful', 'cancelled', 'active.awarded'):
                    django_orm_insert_into_arch_act(ArchiveTender, dict_for_database)

                else:
                    django_orm_insert_into_arch_act(ActiveTender, dict_for_database)
            else:
                django_orm_insert_into_arch_act(ActiveTender, dict_for_database)
        except Exception as e:
            print(f'[INFO from bot# {bot}] XXX Data {total_links[i]} was not added to the database XXX', e, count,
                  link)


def online_processing_active_tenders(tenders_list: list, start_index: int, step: int, bot: int, sleep: float):
    """
    Handling the ActiveTenders table
    :param step:
    :param start_index:
    :param sleep:
    :param bot:
    :param tenders_list: List of all records with all fields from the table in the database (active_tenders)
    :return:
    """

    count = 0
    for i in range(start_index, len(tenders_list), step):
        count += 1
        tender = list(tenders_list[i])
        inner_status = tender.pop()
        db_id = tender.pop(0)
        tender_id = tender[0][31:]
        try:
            dict_tender_for_matching = get_api_data_for_db(tender_id, sleep)
        except Exception as e:
            print(f'[INFO from bot# {bot}] Data {tenders_list[i]} was not collected from the page', e)
        else:
            is_match = check_match(tender, dict_tender_for_matching)

            if inner_status == 'new':
                try:
                    ActiveTender.objects.filter(id=db_id).update(inner_status='old')
                except Exception as e:
                    print(f'[INFO from bot# {bot}] Data was not updated in collector.active_tenders', e)
                else:
                    print(f'[INFO from bot# {bot}] Inner_status was updated in the tender id: {db_id}')

            if dict_tender_for_matching['Статус'] in ('complete', 'unsuccessful', 'cancelled', 'active.awarded'):
                is_tender_replaced = False
                try:
                    django_orm_insert_into_arch_act(ArchiveTender, dict_tender_for_matching)
                except Exception as e:
                    print(f'[INFO from bot# {bot}] Data was not inserted to collector.archive_tenders', e)
                else:
                    is_tender_replaced = True

                if is_tender_replaced:
                    try:
                        ActiveTender.objects.filter(id=db_id).delete()
                    except Exception as e:
                        print(f'[INFO from bot# {bot}] Data was not deleted from collector.active_tenders', e)
                    else:
                        print(f'[INFO from bot# {bot}] Data was deleted from collector.active_tenders')

                    continue

            if not is_match:
                try:
                    dct_filter = {'id': db_id}
                    django_orm_update_arch_act(ActiveTender, dict_tender_for_matching, dct_filter)
                except Exception as e:
                    print(f'[INFO from bot# {bot}] Data {tender_id} was not updated in collector.active_tenders', e)


def manager_for_processing_active_tenders(bot_numbers):
    """
    Processing control manager for the active_tenders table
    :param bot_numbers: - number of threads
    :return:
    """

    while True:
        print('[Processor] Sleeping 7 seconds...')
        time.sleep(7)
        try:
            tenders = list(ActiveTender.objects.all().select_related('winner').values_list(
                'id', 'link', 'status', 'tender_name', 'customer_id', 'initial_price', 'finish_price',
                'winner__name', 'publication_date', 'inner_status').order_by('id'))
        except Exception as e:
            print('[Processor] [INFO] The tenders data has not been collected', e)
        else:
            if tenders:
                print('[Processor] [INFO] The TENDERS DATA has been collected')
                threads = []
                for i in range(bot_numbers):
                    t = threading.Thread(target=online_processing_active_tenders,
                                         args=(tenders, i, bot_numbers, i + 1, i / 10 + 0.2))
                    threads.append(t)
                    t.start()
                for thread in threads:
                    thread.join()


def manager_for_collecting_links(bot_numbers: int):
    """
    Collection of online fresh tenders on the Prozorro site
    :param bot_numbers: number of threads for parsing the list of tenders
    :return: None
    """

    ukraine_time = timezone("Europe/Kiev")
    time_stamp = datetime.now(ukraine_time).timestamp()

    url = f'https://public.api.openprocurement.org/api/2.5/tenders?limit=1000&offset={time_stamp}'
    time.sleep(10)
    steck = [''] * 10000
    while True:
        print('[Collector] NEW ONLINE TENDERS REQUEST...')
        data = make_request(url)
        if data:
            first_level = data.get('data')
            id_list = [dct['id'] for dct in first_level]

            in_steck(steck, id_list)

            url = data.get('next_page').get('uri')

            if first_level:
                index = len(first_level) - 1
                print(first_level[index]['dateModified'])
            else:
                print('[Collector] THERE ARE HAVE NO ANY NEW TENDERS YET...')

            if id_list:
                threads = []
                for i in range(bot_numbers):
                    t = threading.Thread(
                        target=parse_with_tender_id_by_api,
                        args=(id_list, i, bot_numbers, i + 1, i / 10 + 0.1, True)
                    )
                    threads.append(t)
                    t.start()
                for thread in threads:
                    thread.join()

        print('[Collector] SlEEP 5 SECONDS...')
        time.sleep(5)


def make_request(url):
    try:
        response = requests.get(url, verify=False)
        if response.status_code < 300:
            return response.json()
        else:
            print(f"Request failed with status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Request failed: {e}")
    return None


def in_steck(steck_var, id_list_var):
    i = 0
    while i < len(id_list_var):
        if id_list_var[i] not in steck_var:
            steck_var.insert(0, id_list_var[i])
            steck_var.remove(steck_var[-1])
            i += 1
        else:
            id_list_var.remove(id_list_var[i])
