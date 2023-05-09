import json
import unittest
import random
from unittest.mock import patch, MagicMock, PropertyMock

from requests import RequestException
from django.test import TestCase

from tenders.models import ActiveTender, ArchiveTender
from tenders.parsing.json_parse import JsonParse
from tenders.parsing.parsing import parse_with_tender_id_by_api
from tenders.parsing.tools import get_api_data_for_db, reformat_string, check_match

RETURN_DICT = {
            'Веб-посилання': 'https://prozorro.gov.ua/tender/2605149d816d414995eaeaefadbdd4a3',
            'Статус': 'complete',
            'Назва тендеру': 'Фарби автомобільні та супутня продукція',
            'Номер тендеру': 'ДК021:2015:44810000-1',
            'Замовник': "3 ДЕРЖАВНИЙ ПОЖЕЖНО-РЯТУВАЛЬНИЙ ЗАГІН  ГОЛОВНОГО УПРАВЛІННЯ ДЕРЖАВНОЇ СЛУЖБИ УКРАЇНИ З "
                        "НАДЗВИЧАЙНИХ СИТУАЦІЙ У ЧЕРКАСЬКІЙ ОБЛАСТІ",
            'Замовник_ЄДРПОУ': '39209135',
            'Очікувана ціна': 12360.0,
            'Кінцева ціна': 12360.0,
            'Переможець': 'ЛИСЕНКО АНАТОЛІЙ ОЛЕКСІЙОВИЧ',
            'Переможець_ЄДРПОУ': '2420402194',
            'Дата оприлюдення': '2023-04-24',
            'Email замовника': '3dprz_ck@ukr.net'
        }


class ToolsTest(TestCase):
    def setUp(self) -> None:
        self.lst = ["some'string", "'some_string'", "so'me'string", "some_string'"]

    def test_reformat_string(self):
        some_dct = {'key_1': random.choice(self.lst), 'key_2': random.choice(self.lst)}

        reformated_dct = reformat_string(some_dct)

        for i, k in zip(reformated_dct, some_dct):
            self.assertEqual(reformated_dct[i], some_dct[k].replace("'", '"'))


class JsonParseTest(TestCase):
    @staticmethod
    def get_prepared_data():
        with open('django_tenders/tests/response_succ_file.json') as f:
            prepared_data = json.load(f)
        return prepared_data

    def test_get_status(self):
        prepared_data = self.get_prepared_data()
        json_parse = JsonParse(prepared_data)
        result = json_parse.get_status()
        self.assertEqual(result, RETURN_DICT.get('Статус'))

    def test_get_tender_name(self):
        prepared_data = self.get_prepared_data()
        json_parse = JsonParse(prepared_data)
        result = json_parse.get_tender_name()
        self.assertEqual(result, RETURN_DICT.get('Назва тендеру'))

    def test_get_dk_numbers(self):
        prepared_data = self.get_prepared_data()
        json_parse = JsonParse(prepared_data)
        result = json_parse.get_dk_numbers()
        self.assertEqual(result, RETURN_DICT.get('Номер тендеру'))

    def test_get_customer(self):
        prepared_data = self.get_prepared_data()
        json_parse = JsonParse(prepared_data)
        result = json_parse.get_customer()
        self.assertEqual(result, RETURN_DICT.get('Замовник'))

    def test_get_customer_edrpou(self):
        prepared_data = self.get_prepared_data()
        json_parse = JsonParse(prepared_data)
        result = json_parse.get_customer_edrpou()
        self.assertEqual(result, RETURN_DICT.get('Замовник_ЄДРПОУ'))

    def test_get_initial_price(self):
        prepared_data = self.get_prepared_data()
        json_parse = JsonParse(prepared_data)
        result = json_parse.get_initial_price()
        self.assertEqual(result, RETURN_DICT.get('Очікувана ціна'))

    def test_get_finish_price(self):
        prepared_data = self.get_prepared_data()
        json_parse = JsonParse(prepared_data)
        result = json_parse.get_finish_price()
        self.assertEqual(result, RETURN_DICT.get('Кінцева ціна'))

    def test_get_winner(self):
        prepared_data = self.get_prepared_data()
        json_parse = JsonParse(prepared_data)
        result = json_parse.get_winner()
        self.assertEqual(result, RETURN_DICT.get('Переможець'))

    def test_get_winner_edrpou(self):
        prepared_data = self.get_prepared_data()
        json_parse = JsonParse(prepared_data)
        result = json_parse.get_winner_edrpou()
        self.assertEqual(result, RETURN_DICT.get('Переможець_ЄДРПОУ'))

    def test_get_publication_date(self):
        prepared_data = self.get_prepared_data()
        json_parse = JsonParse(prepared_data)
        result = json_parse.get_publication_date()
        self.assertEqual(result, RETURN_DICT.get('Дата оприлюдення'))

    def test_get_customer_email(self):
        prepared_data = self.get_prepared_data()
        json_parse = JsonParse(prepared_data)
        result = json_parse.get_customer_email()
        self.assertEqual(result, RETURN_DICT.get('Email замовника'))


class ToolsUnitTest(unittest.TestCase):
    def get_origin_tender(self):
        self.origin_tender = list(RETURN_DICT.values())
        self.origin_tender.pop(3)
        self.origin_tender.pop(4)
        self.origin_tender.pop(7)
        self.origin_tender.pop()

        return self.origin_tender

    @staticmethod
    def get_mock_objects(requests_mock):
        with open('django_tenders/tests/response_succ_file.json') as f:
            prepared_data = json.load(f)

        req_resp_mock = MagicMock()
        type(req_resp_mock).status_code = PropertyMock(return_value=200)
        type(req_resp_mock).headers = PropertyMock(return_value={'Content-Type': ['application/json']})
        req_resp_mock.json.return_value = prepared_data
        requests_mock.get.return_value = req_resp_mock

    @patch('tenders.parsing.tools.requests')
    def test_get_api_data_for_db_success(self, requests_mock):
        self.get_mock_objects(requests_mock)

        dct = get_api_data_for_db('2605149d816d414995eaeaefadbdd4a3', 0.1)
        self.assertEqual(dct, RETURN_DICT)

    @patch('tenders.parsing.tools.requests')
    def test_get_api_data_for_db_failed_status(self, requests_mock):
        req_resp_mock = MagicMock()
        type(req_resp_mock).status_code = PropertyMock(return_value=400)
        requests_mock.get.return_value = req_resp_mock

        try:
            get_api_data_for_db('2605149d816d414995eaeaefadbdd4a3', 0.1)
        except RequestException as e:
            self.assertEqual(type(e), type(RequestException()))

    @patch('tenders.parsing.tools.requests')
    def test_check_match_true(self, requests_mock):
        origin_tender = self.get_origin_tender()

        self.get_mock_objects(requests_mock)
        dct = get_api_data_for_db('2605149d816d414995eaeaefadbdd4a3', 0.1)

        result = check_match(origin_tender, dct)
        self.assertEqual(result, True)

    @patch('tenders.parsing.tools.requests')
    def test_check_match_false(self, requests_mock):
        origin_tender = self.get_origin_tender()

        self.get_mock_objects(requests_mock)
        dct = get_api_data_for_db('2605149d816d414995eaeaefadbdd4a3', 0.1)
        dct['Статус'] = 'cancelled'

        result = check_match(origin_tender, dct)
        self.assertEqual(result, False)


class ParsingUnitTest(unittest.TestCase):
    @patch('tenders.parsing.tools.requests')
    def test_parse_with_tender_id_by_api_active(self, requests_mock):
        ToolsUnitTest().get_mock_objects(requests_mock)

        parse_with_tender_id_by_api(['2605149d816d414995eaeaefadbdd4a3'], 0, 1, 1, 0.1, False)
        tender = ActiveTender.objects.get(link='https://prozorro.gov.ua/tender/2605149d816d414995eaeaefadbdd4a3')
        self.assertEqual(tender.tender_name, RETURN_DICT.get('Назва тендеру'))

    @patch('tenders.parsing.tools.requests')
    def test_parse_with_tender_id_by_api_archive(self, requests_mock):
        ToolsUnitTest().get_mock_objects(requests_mock)

        parse_with_tender_id_by_api(['2605149d816d414995eaeaefadbdd4a3'], 0, 1, 1, 0.1, True)
        tender = ArchiveTender.objects.get(link='https://prozorro.gov.ua/tender/2605149d816d414995eaeaefadbdd4a3')
        self.assertEqual(tender.tender_name, RETURN_DICT.get('Назва тендеру'))
