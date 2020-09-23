from selenium import webdriver
from time import sleep
from time import strptime
from time import mktime
from csv import writer
from csv import reader
from os import path
from os import remove
from os import rename
from collections import defaultdict
from datetime import datetime
from datetime import date
from calendar import month_name
from glob import glob
from helpful_funcs import find_word
from helpful_funcs import delete_word
from helpful_funcs import join_csvs
from helpful_funcs import add_data_to_csv
from helpful_funcs_2 import pull_validation
from helpful_funcs_2 import validate
from helpful_funcs_2 import join_hist_with_pres
from general_processor import limit_dp
from general_processor import removes_percentage_signs
from general_processor import format_selected_dates
from general_processor import output_func
from general_processor import output2


# AUD: discrepancy of one basis point. Data given to nearest 25 basis points.
# Max = 7bps. Mean = 0.18bps. Std = 0.63bps. Spearman correlation = 0.9995
def aud_func(d_pref, pyc_pref, exec_path):
    file_names = [d_pref + 'f01d.xls', d_pref + 'f01dhist.xls']
    column_index = 3
    int_csv_names = [pyc_pref + 'aud_on_new', pyc_pref + 'aud_on_old']
    final_csv_name = pyc_pref + 'aud_on'

    driver = webdriver.Chrome(executable_path=exec_path)
    # gets historical data
    driver.get('https://www.rba.gov.au/statistics/historical-data.html')
    sleep(5)
    driver.find_element_by_xpath('//*[@id="content"]/ul[5]/li[1]/div/a').click()
    # gets more recent data
    driver.find_element_by_xpath('//*[@id="nav-economic-and-financial"]/li[1]/a').click()
    sleep(5)
    driver.find_element_by_xpath('//*[@id="tables-list"]/ul[6]/li[1]/div[1]/a').click()

    sleep(10)

    output2(file_names, column_index, int_csv_names, final_csv_name)
    driver.close()


# CAD: CAD_on data is an approximation to the nearest 25 basis points, while cad_on_data is more precise;
# Max = 7.6 bps. Mean = 0.46 bps. Std = 0.53bps. Spearman Correlation = 0.9287
def cad_func(d_pref, pyc_pref, exec_path):

    downloaded_file = 'lookup.csv'
    column_index_input = 1
    new_csv_name = pyc_pref + 'cad_on'
    old_data_file_name_input = pyc_pref + 'cad_on'

    driver = webdriver.Chrome(executable_path=exec_path)
    driver.get('https://www.bankofcanada.ca/rates/interest-rates/canadian-interest-rates/')
    # selects option for range
    driver.find_element_by_xpath('//*[@id="rangeType_dates"]').click()
    # finds first date field
    first_date_field = driver.find_element_by_xpath('//*[@id="dFrom"]')
    # gets the date 10 years ago
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    current_day = now.day
    past_year = current_year - 10
    past_date = date(past_year, current_month, current_day).isoformat()
    # fills in the field
    first_date_field.send_keys(past_date)
    # finds last date field
    last_date_field = driver.find_element_by_xpath('//*[@id="dTo"]')
    # gets today's date
    today = date.today()
    date_today_string = today.strftime('%Y-%m-%d')
    # fills field in
    last_date_field.send_keys(date_today_string)
    # selects overnight money market
    driver.find_element_by_xpath('//*[@id="V39050"]').click()
    # submits
    driver.find_element_by_xpath('//*[@id="lookupForm"]/div[4]/button[2]').click()
    sleep(5)
    # downloads csv file
    driver.find_element_by_xpath('//*[@id="cfct-build-39876"]/div/div/div[4]/div/span/a[3]').click()

    sleep(5)

    if path.exists(old_data_file_name_input + '_data.csv'):
        join_hist_with_pres(downloaded_file, column_index_input, new_csv_name, old_data_file_name_input, d_pref)
    else:
        output_func(downloaded_file, column_index_input, new_csv_name)
    if path.exists(d_pref + downloaded_file):
        remove(d_pref + downloaded_file)
    driver.close()


# CHF: maximum discrepancy = 9.6bps. Mean discrepancy = 0.359bps. Std = 0.2447bps. Spearman correlation: 0.9964
def chf_func(d_pref, pyc_pref, exec_path):

    int_csv_name = pyc_pref + 'chf'
    final_csv_name = pyc_pref + 'chf_on'

    driver = webdriver.Chrome(executable_path=exec_path)
    driver.get('https://data.snb.ch/en/topics/ziredev#!/cube/zirepo')
    sleep(2)
    # Deselects all options
    driver.find_element_by_xpath('//*[@id="selectionGroup"]/div[1]/input').click()
    # Selects SARON
    driver.find_element_by_xpath('//*[@id="H0"]').click()
    # Last date set to be the last time the data on the website was updated
    date_published = driver.find_element_by_xpath('//*[@id="publication_info"]')
    date_pub_text = date_published.text
    date_text = (date_pub_text.split())[3]
    # Enters last date in relevant fields
    last_date_field = ['//*[@id="fromDateYear"]', '//*[@id="fromDateMonth"]', '//*[@id="fromDateDay"]']
    last_date = ['1999', '06', '01']
    for l in range(len(last_date)):
        driver.find_element_by_xpath(last_date_field[l]).send_keys(last_date[l])
    # Enters today's date in relevant fields
    today_date_field = ['//*[@id="toDateYear"]', '//*[@id="toDateMonth"]', '//*[@id="toDateDay"]']
    date_recent = date_text.split('-')
    for t in range(len(today_date_field)):
        driver.find_element_by_xpath(today_date_field[t]).send_keys(date_recent[t])
    # Refreshes according to request
    driver.find_element_by_xpath('//*[@id="tableQueryApply"]').click()
    sleep(4)
    # Downloads CSV
    driver.find_element_by_xpath('//*[@id="tableQueryDownloadCsv"]/a').click()
    sleep(2)
    # Gets file by looking for most recent file within Downloads
    list_of_files = glob(d_pref + '*.csv')  # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=path.getctime)
    # Formats downloaded csv to make it digestable by general operations, then digested by general operations
    chf_formatting(latest_file, int_csv_name, final_csv_name, pyc_pref)
    if path.exists(latest_file):
        remove(latest_file)
    if path.exists(int_csv_name):
        remove(int_csv_name)
    driver.close()


def chf_formatting(file_path, int_csv_name, final_csv_name, p_pref):
    columns = defaultdict(list)
    with open(file_path) as f:
        read = reader(f, delimiter=';')
        max_row_count = 0
        row_list = []
        for row in read:
            if len(row) > max_row_count:
                max_row_count = len(row)
        # Tracks back to the start of the csv
        f.seek(0)
        for row1 in read:
            if not row1 == []:
                while len(row1) < max_row_count:
                    row1.append(' ')
                row_list.append(row1)
        for row in row_list:
            for (i, v) in enumerate(row):
                columns[i].append(v)

    dates_init = columns[0]
    data_init = columns[2]
    with open(int_csv_name + '.csv', 'w') as csv_file:
        write = writer(csv_file)
        for x, y in zip(dates_init, data_init):
            write.writerow([x, y])

    output_func(int_csv_name + '.csv', 1, final_csv_name)


# EUR: Max = 16bps. Mean = 0.0033bps. Std = 0.224bps. Spearman correlation = 0.99999
def eur_func(d_pref, pyc_pref, exec_path):

    file_name = 'data.csv'
    column_index = 1
    csv_name = pyc_pref + 'eur_on'

    driver = webdriver.Chrome(executable_path=exec_path)
    driver.get('https://sdw.ecb.europa.eu/quickviewexport.do?SERIES_KEY=198.EON.D.EONIA_TO.RATE&type=csv')
    sleep(5)
    output_func(d_pref + file_name, column_index, csv_name)
    driver.close()


# GBP: Max = 100bps. Mean = 0.92bps. Std = 2.4bps. Spearman correlation: 0.9999981.
# Later entries more accurate than earlier ones.
def gbp_func(d_pref, pyc_pref, exec_path):

    file_name = 'Bank of England  Database.csv'
    column_index = 1
    csv_name = pyc_pref + 'gbp_on'

    driver = webdriver.Chrome(executable_path=exec_path)
    driver.get('https://www.bankofengland.co.uk/boeapps/database/fromshowcolumns.asp?'
               'Travel=NIxSUx&FromSeries=1&ToSeries=50&DAT=ALL&FNY=&CSVF=TT&html.x=191&html.y=39&C=5JK&Filter=N')
    csv_button = driver.find_element_by_xpath('/html/body/div[2]/div/section[2]/div/div[1]/div[1]/a[2]')
    sleep(2)
    csv_button.click()
    sleep(5)

    output_func(d_pref + file_name, column_index, csv_name)

    driver.close()


# JPY: Max = 0.2bps. Mean = 0.0056bps. Std = 0.0243bps. Spearman Correlation = 0.99975
def jpy_func(d_pref, pyc_pref, exec_path):
    driver = webdriver.Chrome(executable_path=exec_path)

    # Gets home page of jpn data
    driver.get('http://www3.boj.or.jp/market/en/menu_m.htm')

    first = driver.find_element_by_xpath('/html/body/ul/li[2]/a[1]').text # str
    second = driver.find_element_by_xpath('/html/body/ul/li[2]/a[2]').text # str

    year_list = [first, second]
    for year in year_list:
        tup = data_from_page_of_link_lists(driver, year)
        dates_text_init = tup[0]
        data_entries_init = tup[1]
        data_entries = limit_dp(removes_percentage_signs(data_entries_init))
        dates_text = format_jpy_dates(dates_text_init, year)
        with open(pyc_pref + 'jpy_' + year + '.csv', 'w') as csv_file:
            write = writer(csv_file)
            for x, y in zip(dates_text, data_entries):
                write.writerow([x, y])
    join_csvs(pyc_pref + 'jpy_' + first + '.csv', pyc_pref + 'jpy_' + second + '.csv', pyc_pref + 'jpy_on_int.csv')
    if path.exists(pyc_pref + 'jpy_on_data.csv'):
        join_csvs(pyc_pref + 'jpy_on_int.csv', pyc_pref + 'jpy_on_data.csv', pyc_pref + 'jpy_on.csv')
        file_path = pyc_pref + 'jpy_on.csv'
        output_func(file_path, 1, pyc_pref + 'jpy_on')
    else:
        output_func(pyc_pref + 'jpy_on_int.csv', 1, pyc_pref + 'jpy_on')

    driver.close()


def jpy_func_short(d_pref, pyc_pref, exec_path):
    csv_name = pyc_pref + 'jpy_on.csv'
    new_csv_name = pyc_pref + 'jpy_on.csv'

    driver = webdriver.Chrome(executable_path=exec_path)

    # Gets home page of jpn data
    driver.get('http://www3.boj.or.jp/market/en/menu_m.htm')

    first = driver.find_element_by_xpath('/html/body/ul/li[2]/a[1]').text  # str
    # second = driver.find_element_by_xpath('/html/body/ul/li[2]/a[2]').text  # str

    validation_tuples = pull_validation(csv_name)
    date_lower = (validation_tuples[-1])[0]
    date_lower_struct = strptime(date_lower, '%Y-%m-%d')
    date_lower_datetime = datetime.fromtimestamp(mktime(date_lower_struct))
    date_lower_year = date_lower_datetime.year
    date_lower_year_str = str(date_lower_year)
    get_incoming_tuples_out = (get_incoming_tuples(driver, date_lower_year_str, date_lower_datetime))
    incoming_tuples = get_incoming_tuples_out[0]
    tuple_counter = get_incoming_tuples_out[1]
    break_counter = 0
    incoming_tuples_formatted = []
    if first != date_lower_year_str:
        year_list = [first, date_lower_year_str]
    else:
        year_list = [date_lower_year_str]
    for tup in incoming_tuples:
        date_formatted = (format_jpy_dates_short(tup[0], year_list[break_counter]))[0]
        data_formatted = str((limit_dp(removes_percentage_signs([tup[1]])))[0])
        incoming_tuples_formatted.append((date_formatted, data_formatted))
        # works only if the data concerned goes over one New Year i.e. two years concerned. Not programmed for if
        # three years are concerned.
        if len(incoming_tuples_formatted) == tuple_counter and break_counter == 0:
            break_counter += 1
    new_tuples = validate(incoming_tuples_formatted, validation_tuples)
    add_data_to_csv(csv_name, new_tuples, new_csv_name)


def get_incoming_tuples(driver, lower_year, date_limit):
    first = driver.find_element_by_xpath('/html/body/ul/li[2]/a[1]').text
    incoming_tuples = []
    outgoing_tuples = []
    if first != lower_year:
        incoming_tuples.append(data_from_page_of_link_lists_short(driver, first))
        number_of_tups_under_first = len(incoming_tuples)
        incoming_tuples.append(
            data_from_page_of_link_lists_short(driver, lower_year, limit_gathering=True, date_limit=date_limit))
    elif first == lower_year:
        incoming_tuples.append(
            data_from_page_of_link_lists_short(driver, lower_year, limit_gathering=True, date_limit=date_limit))
        number_of_tups_under_first = len(incoming_tuples)
    for lst in incoming_tuples:
        for tup in lst:
            outgoing_tuples.append(tup)
    return [outgoing_tuples, number_of_tups_under_first]


def data_from_page_of_link_lists(driver, year):
    data_entries_init = []
    dates_text = []
    data_entry_links_text = []
    driver.find_element_by_link_text(year).click()
    data_entry_links = driver.find_elements_by_tag_name('a')
    for link in data_entry_links:
        data_entry_links_text.append(link.text)
    for link_text in data_entry_links_text:
        if find_word(link_text, 'Uncollateralized Overnight Call Rate'):
            dates_text.append(link_text)
            driver.find_element_by_link_text(link_text).click()
            data_entry = driver.find_elements_by_tag_name(
                'span')  # crucial that find_elements is used (not find_element) to generate an iterable object
            for de in data_entry:
                data_entries_init.append(de.text)
            driver.back()
            # sleep(1)
    driver.back()
    return [dates_text, data_entries_init]


def data_from_page_of_link_lists_short(driver, year, limit_gathering=False, date_limit=None):
    data_entries_init = []
    dates_text = []
    data_entry_links_text = []
    driver.find_element_by_link_text(year).click()
    data_entry_links = driver.find_elements_by_tag_name('a')
    for link in data_entry_links:
        data_entry_links_text.append(link.text)
    if limit_gathering:
        date_limit_str = date_limit.strftime('%b. %d')
    for link_text in data_entry_links_text:
        if find_word(link_text, 'Uncollateralized Overnight Call Rate'):
            dates_text.append(link_text)
            driver.find_element_by_link_text(link_text).click()
            data_entry = driver.find_elements_by_tag_name(
                'span')  # crucial that find_elements is used (not find_element) to generate an iterable object
            for de in data_entry:
                data_entries_init.append(de.text)
            driver.back()
            sleep(1)
        if limit_gathering:
            if find_word(link_text, date_limit_str):
                break
    driver.back()
    return list(zip(dates_text, data_entries_init))


def format_jpy_dates(dates_input, year, dates_from_home_page=False):
    if dates_from_home_page:
        dates_only_list = []
        for date in dates_input:
            step1 = date.replace(',', ' ')
            dates_only_list.append(step1)
    else:
        dates_only_list = []
        for date in dates_input:
            step1 = delete_word(date, 'Uncollateralized Overnight Call Rate (')
            if find_word(step1, '.'):
                step2 = delete_word(step1, '.')
            else:
                step2 = step1
            step3 = delete_word(step2, ')')
            step4 = step3 + ' ' + year
            dates_only_list.append(step4)
    dates_formatted = format_selected_dates(dates_only_list)
    return dates_formatted


def format_jpy_dates_short(datee, year):
    dates_only_list = []
    step1 = delete_word(datee, 'Uncollateralized Overnight Call Rate (')
    if find_word(step1, '.'):
        step2 = delete_word(step1, '.')
    else:
        step2 = step1
    step3 = delete_word(step2, ')')
    step4 = step3 + ' ' + year
    dates_only_list.append(step4)
    dates_formatted = format_selected_dates(dates_only_list)
    return dates_formatted


# SEK: Max = 25bps. Mean = 0.0001bps. Std = 0.49bps. Spearman correlation = 0.999995
def sek_func(d_pref, pyc_pref, exec_path):

    column_index_to_format_init = 3
    column_index_for_pathway = 1
    csv_name = pyc_pref + 'sek_on'

    driver = webdriver.Chrome(executable_path=exec_path)
    driver.get('https://www.riksbank.se/en-gb/statistics/search-interest--exchange-rates/')
    driver.maximize_window()
    # Scrolls down half a window (1080 is a fullHD monitor)
    driver.execute_script("window.scrollTo(0, 540)")
    sleep(5)
    # Dropdown Riksbank interest rates
    driver.find_element_by_xpath('//*[@id="swea-searchform"]/fieldset[1]/div[1]/div[1]/a').click()
    sleep(5)
    # Dropdown Riksbank key interest rates
    driver.find_element_by_xpath('//*[@id="swea-searchform"]/fieldset[1]/div[1]/div[1]/div[2]/a').click()
    sleep(5)
    # Selects repo rate
    driver.find_element_by_xpath('//*[@id="swea-searchform"]/fieldset[1]/div[1]/div[1]/div[2]/div/label[4]').click()
    sleep(5)
    # Past date
    past_date_field = driver.find_element_by_xpath('//*[@id="datetime-from"]')
    past_date_field.clear()
    past_date_field.send_keys('01/01/2009')
    # Toggles dropdown menu so that it disappears
    driver.find_element_by_xpath('//*[@id="swea-searchform"]/fieldset[1]/div[1]/div[1]/a').click()
    driver.execute_script("window.scrollTo(0, 1080)")
    sleep(5)
    # Shows result
    driver.find_element_by_xpath('//*[@id="swea-searchform"]/fieldset[2]/div/button').click()
    sleep(5)
    # Downloads csv
    driver.find_element_by_xpath('//*[@id="main-content"]/div/div[1]/div[1]/article/div/div[3]/div[1]/a[2]').click()

    sleep(8)

    list_of_files = glob(d_pref + '*.csv')  # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=path.getctime)
    swedish_csv_formatter(latest_file, column_index_to_format_init)
    output_func(latest_file, column_index_for_pathway, csv_name)

    driver.close()


def swedish_csv_formatter(file_name, column_index):
    columns = defaultdict(list)
    with open(file_name) as f:
        read = reader(f, delimiter=';')
        for row in read:
            for (i, v) in enumerate(row):
                columns[i].append(v)
    dates = columns[0]
    data = columns[column_index]
    data_new = []
    for dat in data:
        data_new.append(dat.replace(',', '.'))
    with open(file_name, 'w') as f1:
        write = writer(f1)
        for x, y in zip(dates, data_new):
            write.writerow([x, y])


# SGD: Max = 20bps. Mean = 0.01bps. Std: 0.39bps. Spearman correlation: 0.9999992
def sgd_func(d_pref, pyc_pref, exec_path):

    file_name = 'Domestic Interest Rates.csv'
    csv_name = pyc_pref + 'sgd'
    final_csv_name = pyc_pref + 'sgd_on'

    driver = webdriver.Chrome(executable_path=exec_path)
    driver.get('https://secure.mas.gov.sg/dir/domesticinterestrates.aspx')
    sleep(5)
    first_fields_xpath = ['//*[@id="ctl00_ContentPlaceHolder1_StartYearDropDownList"]',
                          '//*[@id="ctl00_ContentPlaceHolder1_StartMonthDropDownList"]',
                          '//*[@id="ctl00_ContentPlaceHolder1_FrequencyDropDownList"]']
    first_fields_entries = ['1987', 'Jan', 'Daily']
    for a in range(len(first_fields_entries)):
        driver.find_element_by_xpath(first_fields_xpath[a]).send_keys(first_fields_entries[a])
    now = datetime.now()
    current_month = month_name[now.month]
    sleep(5)
    second_fields_xpath = ['//*[@id="ctl00_ContentPlaceHolder1_EndYearDropDownList"]',
                           '//*[@id="ctl00_ContentPlaceHolder1_EndMonthDropDownList"]']
    second_fields_entries = [now.year, current_month]
    for b in range(len(second_fields_entries)):
        driver.find_element_by_xpath(second_fields_xpath[b]).send_keys(second_fields_entries[b])
    driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_ColumnsCheckBoxList_9"]').click()
    # Submits
    driver.find_element_by_xpath('//*[@id="ctl00_ContentPlaceHolder1_Button2"]').click()
    sleep(5)

    columns = defaultdict(list)
    file_path = d_pref + file_name
    with open(file_path) as f:
        read = reader(f)
        for row in read:
            if len(row) == 4 and row[2] != '':
                for (i, v) in enumerate(row):
                    columns[i].append(v)
    years = columns[0]
    months = columns[1]
    days = columns[2]
    data = columns[3]
    years_step1 = []
    year_store = ''
    for year in years:
        if year != '':
            year_store = year
        years_step1.append(year_store)
    months_step1 = []
    month_store = []
    for month in months:
        if month != '':
            month_store = month
        months_step1.append(month_store)
    dates_step1 = []
    for i, e in enumerate(years_step1):
        dates_step1.append(e + '-' + months_step1[i] + '-' + days[i])
    data_tuples_list = list(zip(dates_step1, data))
    with open(csv_name + '.csv', 'w') as f1:
        write = writer(f1)
        for tup in data_tuples_list:
            write.writerow(tup)
    output_func(csv_name + '.csv', 1, final_csv_name)
    driver.close()


# USD: Max = 1bps. Mean = 0.0001bps. Std = 0.0145bps. Spearman correlation = 0.9999976
def usd_func(d_pref, pyc_pref, exec_path):

    column_index = 2
    csv_name = pyc_pref + 'usd_on'

    driver = webdriver.Chrome(executable_path=exec_path)
    driver.get('https://apps.newyorkfed.org/markets/autorates/fed%20funds')
    driver.find_element_by_xpath('/html/body/div/div[2]/div[2]/div/table[1]/tbody/tr/td/table[1]/'
                                 'tbody/tr[1]/td/table[2]/tbody/tr/td[1]/p[1]/a[2]').click()
    first_date_field = driver.find_element_by_xpath('/html/body/div/div[2]/div[2]/div/table/tbody/'
                                                    'tr/td/div/table/tbody/tr/td/form/table[1]/tbody/tr[3]/td/input[1]')
    first_date_field.send_keys('07/03/2000')
    last_date_field = driver.find_element_by_xpath('/html/body/div/div[2]/div[2]/div/table/tbody/'
                                                   'tr/td/div/table/tbody/tr/td/form/table[1]/tbody/tr[3]/td/input[2]')
    # gets today's date and writes it in the necessary fashion
    today = date.today()
    date_today_string = today.strftime('%m/%d/%Y')
    # writes today's date in the right field
    last_date_field.send_keys(date_today_string)
    # clicks find
    driver.find_element_by_xpath('/html/body/div/div[2]/div[2]/div/table/tbody/tr/td/div/table/tbody/'
                                 'tr/td/form/table[2]/tbody/tr[3]/td/input').click()
    # clicks the Excel button
    driver.find_element_by_xpath('/html/body/div/div[2]/div[2]/div/table/tbody/tr/td/div[1]/table/tbody/'
                                 'tr/td/table/tbody/tr/td/table[1]/tbody/tr[3]/td/table/tbody/tr/td[2]/a[1]').click()
    sleep(5)

    # * means all if need specific format then *.csv
    list_of_files = glob(d_pref + '*.xls')
    latest_file = max(list_of_files, key=path.getctime)
    output_func(latest_file, column_index, csv_name)

    driver.close()
