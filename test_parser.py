from src.quote import YahooHistoricalPricesParser, get_raw_page
import unittest

EXPECTED_NUM_COLUMNS_HISTORICAL_PRICES = 7


class TestParser(unittest.TestCase):
    raw = None
    parser = None

    def setUp(self):
        self.raw = get_raw_page("INTU")
        self.parser = YahooHistoricalPricesParser()

    def test_parsed_table_heads(self):
        self.parser.reset()
        self.parser.feed(self.raw)
        self.assertEqual(len(self.parser.get_table_heads()), EXPECTED_NUM_COLUMNS_HISTORICAL_PRICES)
        self.assertIn("Date", self.parser.get_table_heads())
        self.assertIn("Open", self.parser.get_table_heads())
        self.assertIn("High", self.parser.get_table_heads())
        self.assertIn("Low", self.parser.get_table_heads())
        self.assertIn("Close*", self.parser.get_table_heads())
        self.assertIn("Adj Close**", self.parser.get_table_heads())
        self.assertIn("Volume", self.parser.get_table_heads())

    def test_parsed_time_series(self):
        self.parser.reset()
        self.parser.feed(self.raw)
        num_valid_entries = 0
        for session in self.parser.get_time_series_data():
            if len(session) == EXPECTED_NUM_COLUMNS_HISTORICAL_PRICES:
                num_valid_entries += 1
        self.assertGreaterEqual(num_valid_entries, 1)
