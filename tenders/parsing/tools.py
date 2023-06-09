import time

import requests
from requests import RequestException

from tenders.models import DKNumber, Customer, Winner
from tenders.parsing.json_parse import JsonParse


def reformat_string(dct: dict) -> dict:
    """
    Функция заменяет одинарные кавычки на двойные в строковых значениях
    :param dct: dict
    :return: dict
    """
    for i in dct:
        if isinstance(dct[i], str) and i.split(' ')[0] not in ['Строк', 'Дата']:
            dct[i] = dct[i].replace("'", '"')
    return dct


def get_api_data_for_db(tender_id, sleep):
    """
    Функция запрашивает данные по определенному тендеру (tender_id) через API call. Парсит данные ответа в словарь.
    :param tender_id: str
    :param sleep: float
    :return: dict
    """

    dict_for_database = {}
    time.sleep(sleep)
    url = f'https://public.api.openprocurement.org/api/2.5/tenders/{tender_id}'
    try:
        response = requests.get(url, verify=False)
    except Exception as e:
        print(e)
    else:
        if 300 > response.status_code >= 200:
            if 'application/json' in response.headers.get('Content-Type', ''):
                data = response.json()
                json_parse = JsonParse(data)

                dict_for_database['Веб-посилання'] = f'https://prozorro.gov.ua/tender/{tender_id}'
                dict_for_database['Статус'] = json_parse.get_status()
                dict_for_database['Назва тендеру'] = json_parse.get_tender_name()
                dict_for_database['Номер тендеру'] = json_parse.get_dk_numbers()
                dict_for_database['Замовник'] = json_parse.get_customer()
                dict_for_database['Замовник_ЄДРПОУ'] = json_parse.get_customer_edrpou()
                dict_for_database['Очікувана ціна'] = json_parse.get_initial_price()
                dict_for_database['Кінцева ціна'] = json_parse.get_finish_price()
                dict_for_database['Переможець'] = json_parse.get_winner()
                dict_for_database['Переможець_ЄДРПОУ'] = json_parse.get_winner_edrpou()
                dict_for_database['Дата оприлюдення'] = json_parse.get_publication_date()
                dict_for_database['Email замовника'] = json_parse.get_customer_email()

                dict_for_database = reformat_string(dict_for_database)

                return dict_for_database
        else:
            raise RequestException


def django_orm_insert_into_arch_act(model, dict_for_database):
    customer, _ = Customer.objects.get_or_create(
        edrpou=dict_for_database['Замовник_ЄДРПОУ'],
        defaults={'name': dict_for_database['Замовник'],
                  'person_contact': dict_for_database['Email замовника']}
    )

    winner, _ = Winner.objects.get_or_create(
        name=dict_for_database['Переможець'],
    )

    tender = model.objects.create(
        link=dict_for_database['Веб-посилання'],
        status=dict_for_database['Статус'],
        tender_name=dict_for_database['Назва тендеру'],
        customer=customer,
        initial_price=dict_for_database['Очікувана ціна'],
        finish_price=dict_for_database['Кінцева ціна'],
        winner=winner,
        publication_date=dict_for_database['Дата оприлюдення']
    )

    dk_numbers = dict_for_database['Номер тендеру'].split(', ')
    dk_numbers = DKNumber.objects.values_list('id', flat=True).filter(dk__in=dk_numbers)

    tender.dk_numbers.set(DKNumber.objects.filter(id__in=dk_numbers))
    print(f'[INFO] The data was successfully inserted into {model}')


def django_orm_update_arch_act(model, dict_for_database, dct_filter: dict):
    winner, _ = Winner.objects.get_or_create(
        name=dict_for_database['Переможець'],
    )

    model.objects.filter(**dct_filter).update(
        link=dict_for_database['Веб-посилання'],
        status=dict_for_database['Статус'],
        tender_name=dict_for_database['Назва тендеру'],
        initial_price=dict_for_database['Очікувана ціна'],
        finish_price=dict_for_database['Кінцева ціна'],
        winner=winner,
        publication_date=dict_for_database['Дата оприлюдення']
    )

    print(f'[INFO] The data was successfully updated in {model}')


def check_match(origin_tender, new_tender: dict):
    origin_tender = origin_tender.copy()

    origin_tender[7] = f"{str(origin_tender[7])}" if origin_tender[7] is not None else None
    origin_tender[4] = float(origin_tender[4])
    origin_tender[5] = float(origin_tender[5])
    origin_tender.pop(3)
    # origin_tender.pop(5)

    new_tender = new_tender.copy()
    new_tender.pop('Номер тендеру')
    new_tender.pop('Замовник')
    new_tender.pop('Замовник_ЄДРПОУ')
    new_tender.pop('Переможець_ЄДРПОУ')
    new_tender.pop('Email замовника')
    list_new_tender = list(new_tender.values())

    return origin_tender == list_new_tender
