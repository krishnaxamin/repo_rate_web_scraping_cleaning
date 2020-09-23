from on_rates_currencies import aud_func
from on_rates_currencies import cad_func
from on_rates_currencies import chf_func
from on_rates_currencies import eur_func
from on_rates_currencies import gbp_func
from on_rates_currencies import jpy_func
from on_rates_currencies import jpy_func_short
from on_rates_currencies import sek_func
from on_rates_currencies import sgd_func
from on_rates_currencies import usd_func
from time import time

""" Need to install chromedriver.exe. Can be found at chromedriver.chromium.org/downloads. ChromeDriver 79.0.3945.36 
was used, but different ones are required based on what version of Chrome is being run on your machine. 
Other things needed:
    selenium
    pandas (if not had already)
    dateutil (if not had already)
    
To set number of decimal places, go to general_processor and alter the global variable decimal_place_str.
To set names for output csvs, go to on_rates_currencies and alter the variable there (oft within the 
first few lines of each function).
Column index is important for pulling the correct data out of csv/excel files with multiple data sets. Can be found
through manual inspection of the downloaded file. 
_short functions pull only the newest data from the websites and append it to an existing file, after checking any 
overlapping data matches. 

Change downloads_prefix to specify where files downloaded from your browser end up. 
Change directory_prefix to specify directory path.
Change executive_path to specify path to chromedriver.exe.
"""

# specifies where downloaded files end up
downloads_prefix = r'C:\\Users\\krish\\Downloads\\'
# specifies directory where all the csvs are - final output
directory_prefix = r'C:\\Users\\krish\\PycharmProjects\\2RSq\\'
# specifies path to access chromedriver.exe
executive_path = r'C:\Users\krish\PycharmProjects\2RSq\Files to Transfer\chromedriver.exe'

func_list = [[aud_func, True], [cad_func, True], [chf_func, True], [eur_func, True], [gbp_func, True],
             [jpy_func, True], [jpy_func_short, False], [sek_func, True], [sgd_func, True], [usd_func, True]]

func_str_list = ['AUD', 'CAD', 'CHF', 'EUR', 'GBP', 'JPY', 'JPY', 'SEK', 'SGD', 'USD']

# provides timings for each process and for the whole programme
start = time()
for i, tup in enumerate(func_list):
    if tup[1]:
        start_func = time()
        tup[0](downloads_prefix, directory_prefix, executive_path)
        end_func = time()
        print(func_str_list[i] + ': ' + str(end_func-start_func))
end = time()
print('Total Time: ' + str(end-start))
