# A Python Script Tool for Scraping Stock Prices

## Usage
The tool will scrape Yahoo Finance page to scrape the historic prices of a given stock and display the open, close, high and low prices of the most recent trading session. The tool could be run on the command line with Python 3.8. The user need to specify the tick symbol of the stock as an command line argument to the program. Here is an example of running the script with stock symbol "INTU" provided.

``` 
% python quote.py INTU 
{'close': '372.34',
 'date': 'Jan 11, 2021',
 'high': '376.76',
 'low': '366.54',
 'open': '376.13'}
```

## Design
The tool leverages built-in libraries of Python 3.8 to scrape the raw data from the webpage and parse it to fetch the useful information.

`http.client` is used for sending https request to Yahoo finance to get the raw data. The tool extended the `HTMLParser` class to parse the historical prices table in the raw page. The implemented parser will convert the entire historic prices table into two lists: the first list consists of all the table head keys, and the second list is a list of price information of trading sessions in chronicle order. The values in the price information of one trading session will conform to the same order of the table keys in the first list.

It is noticed during testing that if there is a special event involved for a stock (e.g. dividends), it will be listed as a separate trading session in the historic prices table. In those cases, the parser will skip those lines when constructing the time series price information.

## Error Handling
The tool handles the following error scenarios:
1. The provided stock tick symbol is illegal, specifically the input is of illegal length or contains illegal characters.
2. The provided stock tick symbol passes the early validation but is not a valid symbol in Yahoo Finance, in those cases, Yahoo Finance has a 302 http response code, and the tool handles this specifically.
3. It is not able for the machine running this tool to get a connection to Yahoo Finance. This could be caused by connectivity issues of the machine, SSL errors, DNS errors or Yahoo Finance not being available. The tool specifically handles those scenarios, and the error message should indicate the root cause of the connectivity issue. 
4. Although the implementation of the parser tries to be robust with the changes made to the Yahoo Finance page, more significant changes to the response of the raw page could break the parser, the parser tries to throw relevant exception in these kinds of scenarios. Moreover, the unit test for the parser could detect the schema changes for the source page.