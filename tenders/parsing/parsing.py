from datetime import datetime
import threading
from pytz import timezone
from tenders.models import ArchiveTender, ActiveTender, Customer
# from tenders.parsing.tasks import user_notification
from tenders.parsing.tools import *
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def parse_with_tender_id_by_api(total_links, start, step, bot, sleep, is_archivating=False):
    """
    Парсинг тендеров по id (через API), разделение на активные и завершенные в БД
    :param sleep:
    :param bot: int - Порядкоый номер потока
    :param total_links: list - список id
    :param start: int - стартовый индекс чтения списка total_links
    :param step: int - шаг чтения списка total_links
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
                    # prozorro_api_post_tender('archive', dict_for_database, token, host)

                else:
                    django_orm_insert_into_arch_act(ActiveTender, dict_for_database)
                    # prozorro_api_post_tender('active', dict_for_database, token, host)
            else:
                django_orm_insert_into_arch_act(ActiveTender, dict_for_database)
                # prozorro_api_post_tender('active', dict_for_database, token, host)

            # print(f'[INFO from bot# {bot}] Data {total_links[i]} was added to the active_tenders', count)
        except Exception as e:
            print(f'[INFO from bot# {bot}] XXX Data {total_links[i]} was not added to the database XXX', e, count,
                  link)


def online_processing_active_tenders(tenders_list: list, start_index: int, step: int, bot: int, sleep: float):
    """

    :param step:
    :param start_index:
    :param sleep:
    :param bot:
    :param tenders_list: Список всех записей со всеми полями из таблицы в БД (active_tenders)
    :return:
    """

    # messages = [
    #     'Здравствуйте! Уведомляем Вас о появившемся новом тендере в интересующем Вас разделе. Рекомендуем ознакомиться: ',
    #     'Здравствуйте! Уведомляем Вас о завершении тендера в интересующем Вас разделе: ',
    #     'Здравствуйте! Уведомляем Вас о внесении изменений в тендер в интересующем Вас разделе: ',
    # ]

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
            dk_numbers = dict_tender_for_matching['Номер тендеру'].split(', ')
            link = dict_tender_for_matching['Веб-посилання']
            is_match = check_match(tender, dict_tender_for_matching)

            if inner_status == 'new':
                # user_notification(dk_numbers, link, messages[0])
                try:
                    ActiveTender.objects.filter(id=db_id).update(inner_status='old')
                except Exception as e:
                    print(f'[INFO from bot# {bot}] Data was not updated in collector.active_tenders', e)

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

                    # user_notification(dk_numbers, link, messages[1])
                    continue

            if not is_match:
                try:
                    dct_filter = {'id': db_id}
                    django_orm_update_arch_act(ActiveTender, dict_tender_for_matching, dct_filter)
                except Exception as e:
                    print(f'[INFO from bot# {bot}] Data {tender_id} was not updated in collector.active_tenders', e)

                # user_notification(dk_numbers, link, messages[2])


def manager_for_processing_active_tenders(bot_numbers):
    """
    Менеджер управления обработкой таблицы active_tenders
    :param bot_numbers: - количество потоков
    :return:
    """

    while True:
        print('[Processor] Sleeping 7 seconds...')
        time.sleep(7)
        try:
            tenders = list(ActiveTender.objects.all().select_related('winner').values_list(
                'id', 'link', 'status', 'tender_name', 'customer_id', 'initial_price', 'finish_price',
                'winner__winner_name', 'publication_date', 'inner_status').order_by('id'))
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
    Сбор онлайн свежих тендеров на площадке Prozorro
    :param bot_numbers: количество потоков для парсинга списка тендеров
    :return: None
    """

    ukraine_time = timezone("Europe/Kiev")
    time_stamp = datetime.now(ukraine_time).timestamp()

    url = f'https://public.api.openprocurement.org/api/2.5/tenders?limit=1000&offset={time_stamp}'
    time.sleep(10)
    steck = [''] * 10000
    while True:
        print('[Collector] NEW ONLINE TENDERS REQUEST...')
        try:
            response = requests.get(url, verify=False)
        except Exception as e:
            print(e)
            response = None

        if response:
            status_code = response.status_code
            print(f'[Collector] Status_code = {status_code}')
            if 300 > response.status_code >= 200:
                if 'application/json' in response.headers.get('Content-Type', ''):
                    try:
                        data = response.json()
                    except AttributeError as e:
                        print(e)
                        print("[Collector] [INFO] XXX The response does not have JSON data XXX")
                    else:
                        first_level = data.get('data')
                        id_list = [dct['id'] for dct in first_level]

                        i = 0
                        while i < len(id_list):
                            if id_list[i] not in steck:
                                steck.insert(0, id_list[i])
                                steck.remove(steck[-1])
                                i += 1
                            else:
                                id_list.remove(id_list[i])

                        url = data.get('next_page').get('uri')
                        # print(f'[Collector] NEXT URL: {url}')
                        # print(id_list)

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
