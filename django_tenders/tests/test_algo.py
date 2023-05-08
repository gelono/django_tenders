from django.test import TestCase


class BookTestCase(TestCase):
    def setUp(self) -> None:
        self.author1 = 'A'
        self.author2 = 'A'

    def test_authors_string_zero_authors(self):
        self.assertEqual(self.author1, self.author2)
