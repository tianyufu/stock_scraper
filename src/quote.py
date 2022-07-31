from html.parser import HTMLParser
from http import HTTPStatus, client
import pprint
import sys

YAHOO_FINANCE_URL = "finance.yahoo.com"
YAHOO_FINANCE_QUERY = "/quote/{}/history?p={}"


class YahooHistoricalPricesParser(HTMLParser):
    """
    Parser to get structured time series data of the stock from the historical prices table on
    Yahoo Finance page.
    """

    _parsing_quote_table = False
    _parsing_table_heads = False
    _parsing_table_body = False

    _parsed_table_heads = []
    _day_entry = []
    _time_series_data = []

    def reset(self):
        """Overrides the method in HTMLParser"""
        super(YahooHistoricalPricesParser, self).reset()
        self._parsing_quote_table = False
        self._parsing_table_heads = False
        self._parsing_table_body = False
        self._parsed_table_heads = []
        self._day_entry = []
        self._time_series_data = []

    def handle_starttag(self, tag, attrs):
        """Overrides the method in HTMLParser"""

        if self._parsing_quote_table:
            if tag == 'thead':
                self._parsing_table_heads = True
            elif tag == 'tbody':
                self._parsing_table_body = True
            return

        if tag == 'table':
            for attr in attrs:
                if attr[1] == 'historical-prices':
                    self._parsing_quote_table = True

    def handle_endtag(self, tag):
        """Overrides the method in HTMLParser"""

        if not self._parsing_quote_table:
            return

        if tag == 'thead':
            self._parsing_table_heads = False
        elif tag == 'tbody':
            self._parsing_table_body = False
        elif tag == 'table':
            self._parsing_quote_table = False
        elif tag == 'tr' and not self._parsing_table_heads:
            self._time_series_data.append(self._day_entry)
            self._day_entry = []

    def handle_data(self, data):
        """Overrides the method in HTMLParser"""

        if not self._parsing_quote_table:
            return

        if self._parsing_table_heads:
            self._parsed_table_heads.append(data)
        elif self._parsing_table_body:
            self._day_entry.append(data)

    def get_time_series_data(self):
        """Returns the time series data of the stock as a list."""

        return self._time_series_data

    def get_table_heads(self):
        """Returns table heads of the historic prices data table as a list."""

        return self._parsed_table_heads


def quote(symbol):
    """
    Get the open, close, low and high prices of the specified stock today. If there has not been a
    trading session for the stock today, the method will return the price information of the
    most recent trading session.

    :param symbol: tick symbol of the stock
    :return: the open, close, low and high prices of the specified stock
    """
    validate_tick_symbol(symbol)
    parser = YahooHistoricalPricesParser()
    parser.feed(get_raw_page(symbol))
    return _serve_result(parser.get_table_heads(), parser.get_time_series_data())


def validate_tick_symbol(symbol):
    """
    An early validation of the input stock tick symbol and filter malicious invocations.

    :param symbol: the input stock symbol
    :return: None
    """
    if symbol is None or len(symbol) == 0 or len(symbol) > 128:
        raise ValueError("Invalid symbol: {}".format(symbol))
    for ch in symbol:
        if ord(ch) <= 32 or ord(ch) >= 127:
            raise ValueError("Illegal character {} found in specified symbol".format(ch))


def get_raw_page(symbol):
    """
    Get the raw html page of the quoted stock on Yahoo finance.

    :param symbol: the input stock symbol
    :return: the raw html page that contains the historical price data of the stock
    """
    conn = client.HTTPSConnection(YAHOO_FINANCE_URL)
    try:
        conn.request("GET", YAHOO_FINANCE_QUERY.format(symbol, symbol))
    except (OSError, ValueError) as err:
        raise RuntimeError('Cannot connect to {}: {}'.format(YAHOO_FINANCE_URL, str(err)))

    response = conn.getresponse()

    if response.status != HTTPStatus.OK:
        # Yahoo finance redirects when the stock symbol is invalid
        if response.status == HTTPStatus.FOUND:
            raise ValueError('Invalid stock tick symbol:', symbol)
        else:
            raise RuntimeError(
                "Got {} response code from {}.".format(response.status, YAHOO_FINANCE_URL))

    return response.read().decode('utf-8')


def _serve_result(table_heads, time_series):
    """
    Assemble the output that contains the high, low, open and close prices of the most recent
    trading session.

    :param table_heads: the table heads parsed from the historical prices table on the webpage
    :param time_series: the time series list parsed from the historical prices table
    :return: a dictionary consists of date of the most recent trading session and price information
    """

    for session in time_series:
        # There are some cases the table has dividend entries that does not conform to the
        # table head, those lines should be skipped.
        if len(session) != len(table_heads):
            continue

        # Return the most recent trading session information.
        try:
            return {'date': session[table_heads.index('Date')],
                    'high': session[table_heads.index('High')],
                    'low': session[table_heads.index('Low')],
                    'open': session[table_heads.index('Open')],
                    'close': session[table_heads.index('Close*')]}
        except ValueError as err:
            raise RuntimeError(
                'Historical prices table schema in the scraped page has been changed:', err)

    # if it reaches here, it means the time series table does not contain historical price data
    # for the stock
    raise RuntimeError("Cannot find historical prices data for the stock.")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        if len(sys.argv) < 2:
            print("Please specify the tick symbol of the stock as an argument.")
        elif len(sys.argv) > 2:
            print("The script only accepts a stock symbol as one argument.")
        sys.exit(1)

    pp = pprint.PrettyPrinter()
    try:
        pp.pprint(quote(sys.argv[1]))
    except (ValueError, RuntimeError) as e:
        print(str(e))
        sys.exit(1)
