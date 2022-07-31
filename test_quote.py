from src import quote
import unittest


class TestQuote(unittest.TestCase):

    def test_quote_success(self):
        result = quote.quote('INTU')
        self.assertTrue(result.get('date') is not None)
        self.assertTrue(float(result.get('high')) >= 0)
        self.assertTrue(float(result.get('low')) >= 0)
        self.assertTrue(float(result.get('open')) >= 0)
        self.assertTrue(float(result.get('close')) >= 0)

    def test_quote_lowercase_success(self):
        result = quote.quote('isrg')
        self.assertTrue(result.get('date') is not None)
        self.assertTrue(float(result.get('high')) >= 0)
        self.assertTrue(float(result.get('low')) >= 0)
        self.assertTrue(float(result.get('open')) >= 0)
        self.assertTrue(float(result.get('close')) >= 0)

    def test_quote_invalid_symbol(self):
        self.assertRaises(ValueError, lambda: quote.quote('INVALID'))

    def test_quote_empty_symbol(self):
        self.assertRaises(ValueError, lambda: quote.quote(''))

    def test_quote_illegal_symbol(self):
        self.assertRaises(ValueError, lambda: quote.quote(' :('))

    def test_quote_None_symbol(self):
        self.assertRaises(ValueError, lambda: quote.quote(None))
