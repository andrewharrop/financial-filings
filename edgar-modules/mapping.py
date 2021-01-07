"""
    The purpose of this file is to manage everything to do with retrieving CIK's, and updating a local list of CIK's.

    The end goal is to input a ticker, and output a CIK or None.

    Mapping also manages the retrieval of any other useful data that does not require further processing

    There are some examples at the bottom of the file, although this file will not have to be run by itself very often.
"""
import os
import json
import requests

from bs4 import BeautifulSoup

# This class deals with 
class Mapping:
    def __init__(self):

        # Must remain constant:
        self.ticker_CIK = './mapping/tickers.json'
        self.name_CIK = './mapping/names.json'
        self.filetypes = './mapping/filetypes.txt'
        self.ticker_data = 'https://www.sec.gov/include/ticker.txt'
        self.name_data = 'https://www.sec.gov/Archives/edgar/cik-lookup-data.txt'

        if not (os.path.exists('mapping')):
            os.mkdir('mapping')

    def update_ticker_file(self):
        if os.path.exists(self.ticker_CIK):
            os.remove(self.ticker_CIK)

        ticker_text = requests.get(self.ticker_data).text
        split_tickers = ticker_text.split('\n')

        with open(self.ticker_CIK, 'w') as ticker_file:
            ticker_ds = {}
            for line in split_tickers:
                try:
                    split_line = line.split('\t')
                    ticker_ds[split_line[0]] = split_line[1]
                except AttributeError:
                    error_message = f'Error with this line:{line}'
                    # Remove in production
                    print(error_message)
            json.dump(ticker_ds, ticker_file)

    def update_name_file(self):
        if os.path.exists(self.name_CIK):
            os.remove(self.name_CIK)

        name_text = requests.get(self.name_data).text
        split_names = name_text.split('\n')

        with open(self.name_CIK, 'w') as name_file:
            name_ds = {}
            for line in split_names:
                try:
                    company_data_list = line.split(':')
                    if len(company_data_list) > 2:
                        name_ds[company_data_list[0]] = company_data_list[1]
                except AttributeError:
                    error_message = f'Error with this line:{line}'

                    # Remove in production
                    print(error_message)

            json.dump(name_ds, name_file)

    def update_form_types(self):
        file = requests.get('https://www.sec.gov/forms').content
        soup = BeautifulSoup(file, 'html.parser')

        table = soup.find('table')
        body = table.find('tbody')
        if os.path.exists(self.filetypes):
            os.remove(self.filetypes)
        with open(self.filetypes, 'w') as df:
            for row in body:
                if row.find('td') != -1:
                    value = ((row.find('td').text.split(':')[1]).strip())
                    if value != 'n/a':
                        if value:
                            df.write(value + '\n')
            df.close()

    def get_filings(self):
        far = []
        try:
            with open(self.filetypes, 'r') as file:
                file = file.read()
                file = file.split('\n')
                for item in file:
                    if item != '\n':
                        if item:
                            far.append(item)
                return far
        except FileNotFoundError:
            message = "Make sure to run update form types at least once"

    def filings(self, filing_type):
        if str(filing_type).upper() in self.get_filings():
            return str(filing_type).upper()
        else:
            return None

    def ticker(self, ticker):
        if os.path.exists(self.ticker_CIK):
            try:
                with open(self.ticker_CIK, 'r') as ticker_CIKs:
                    ticker = ticker.lower()
                    data = json.load(ticker_CIKs)[ticker]
                ticker_CIKs.close()
                return data
            except KeyError:
                ticker_CIKs.close()
                error_message = 'Error in CIK_from_ticker: Keyerror'
                return None
        message = (
            'Error: No file exists that contains the CIK-ticker relationships.  Run retrieve_ticker_map() to fix this')
        return None

    def name(self, name):
        if os.path.exists(self.name_CIK):
            try:
                with open(self.name_CIK, 'r') as name_CIKs:
                    data = json.load(name_CIKs)[name.upper()]
                    return data
            except KeyError:
                return None
        return None




''' 
    This function takes a very long time to run.  
    It iterates through the ticker file, and for each ticker iterates through the name file.  
    Returns a ticker-name pair dict
'''
def ticker_map():
    t_dict = {}
    t_file = json.loads(open('../../data-storage/edgar_ticker_CIK.json', 'r').read())
    n_file = json.loads(open('../../data-storage/edgar_name_CIK.json', 'r').read())
    for item in t_file:
        ticker_dic = int(t_file[item])

        for name in n_file:
            try:
                ncik = (int(n_file[name]))
                if ncik==ticker_dic:
                    t_dict[item]=name
                    break
            except ValueError:
                pass

            # if ticker_dic == name_cik:
            #     print(name)

    print(t_dict)


"""

    Examples:

    
        Create mapping instance:
        my_map = Mapping()

        # Create or update a json file containing all tickers accepted by the SEC. Matched up with a CIK, which is a unique ID:
        my_map.update_ticker_file()

        # Create or update a json file containing all company names registered with the SEC. Matched up with a CIK, which is a unique ID:
        my_map.update_name_file()

        # Create or update a json file with name-CIK pairs associated with the SEC:
        my_map.update_name_file()

        # Enumerate filing types.  Returns a list of filing types:
        my_map.get_filings()

        # Get the CIK given ticker input, in this case the ticker is 'tsla':
        my_map.ticker('tsla')

        # Get the CIK given name input, in this case the ticker is "1-800-JACKPOT INC":
        my_map.name("1-800-JACKPOT INC")

        If you would like to see this in action, try running this section:
            my_map = Mapping()
            my_map.update_ticker_file()
            my_map.update_name_file()
            my_map.update_form_types()
            print(my_map.get_filings())
            print(my_map.ticker('tsla'))
            my_map.name("1-800-JACKPOT INC")
"""

my_map = Mapping()
my_map.update_ticker_file()
my_map.update_name_file()
my_map.update_form_types()
print(my_map.get_filings())
print(my_map.ticker('tsla'))
my_map.name("1-800-JACKPOT INC")