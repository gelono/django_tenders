from google.oauth2 import service_account
from googleapiclient.discovery import build


# The ID and range of a sample spreadsheet.
from tenders.models import ActiveTender

SAMPLE_SPREADSHEET_ID = '1dWgacL7nhfgSLLjtzhlNfDo1O9j2bsiN2puOlVi-TC4'
SAMPLE_RANGE_NAME = 'Лист1!A2:E'


def get_service():
    credentials = service_account.Credentials.from_service_account_file('django_tenders/service_account.json')
    service = build('sheets', 'v4', credentials=credentials)

    return service


def read_from_google_sheets():
    service = get_service()

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    print(values)


def write_from_google_sheets(tenders: [ActiveTender]):
    service = get_service()

    # Call the Sheets API
    sheet = service.spreadsheets()

    values = [
        [tender.link, tender.status, tender.tender_name, tender.customer.name]
        for tender in tenders
    ]

    result = sheet.values().update(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                   range=SAMPLE_RANGE_NAME,
                                   valueInputOption='USER_ENTERED',
                                   body={'values': values}
                                   ).execute()

    print(result)
