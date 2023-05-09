class JsonParse:
    data: dict = None

    def __init__(self, data: dict):
        self.data = data

    def get_status(self):
        return self.data.get('data', {}).get('status', 'Немає даних')

    def get_tender_name(self):
        return self.data.get('data', {}).get('title', 'Немає даних')

    def get_dk_numbers(self):
        dk_numbers = set()
        dk_list = self.data.get('data', {}).get('items', [])
        for i in dk_list:
            dk = i.get('classification', {}).get('scheme', 'Немає даних') + ':2015:' + i.get(
                'classification', {}).get('id', 'Немає даних')
            dk_numbers.add(dk)
        dk_numbers = list(dk_numbers)
        dk_numbers = ', '.join(dk_numbers)

        return dk_numbers

    def get_customer(self):
        return self.data.get('data', {}).get('procuringEntity', {}).get('name', 'Немає даних')

    def get_customer_edrpou(self):
        return self.data.get('data', {}).get('procuringEntity', {}).get('identifier', {}).get('id', 'Немає даних')

    def get_initial_price(self):
        return float(self.data.get('data', {}).get('value', {}).get('amount', 0))

    def get_finish_price(self):
        return float(self.data.get('data', {}).get('awards', [{}])[-1].get('value', {}).get('amount', 0))

    def get_winner(self):
        return self.data.get('data', {}).get('awards', [{}])[-1].get('suppliers', [{}])[-1].get('name', 'Немає даних')

    def get_winner_edrpou(self):
        return self.data.get('data', {}).get('awards', [{}])[-1].get('suppliers', [{}])[-1].get('identifier', {}).get(
            'id', 'Немає даних')

    def get_publication_date(self):
        date_created = self.data.get('data', {}).get('dateCreated', None)
        if date_created is not None:
            date_created = date_created[:10]

        return date_created

    def get_customer_email(self):
        return self.data.get('data', {}).get('procuringEntity', {}).get('contactPoint', {}).get('email', 'Немає даних')
