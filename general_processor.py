from csv import writer
from pandas import read_csv
from pandas import read_excel
from pandas import DataFrame
from os import rename
from os import remove
from os import path
from decimal import Decimal
from decimal import ROUND_HALF_UP
from re import compile
from datetime import datetime
from dateutil import parser
from helpful_funcs import find_word
from helpful_funcs import join_csvs
from helpful_funcs import delete_word
from helpful_funcs import equalise_rows

""" Process: 
        select only relevant data (date_block_dataframe) 
        -> sort the selected data based on type of data: Bank holiday, nan, actual data, miscellaneous (data_sorter)
        -> format the dates and data and write to a csv (output_func/output2)
output_func vs output2 determined """

decimal_place_str = '0.00001'


# creates initial dataframe from csv
def create_dataframe_from_csv(file_path):
    equalise_rows(file_path)
    df = read_csv(file_path, header=None, encoding='cp1252')  # CHANGED FOR AUS ONLY, ACHTUNG!!! Seems to work with other monies
    return df


# creates initial df from excel files
def create_dataframe_from_xls(file_path):
    df = read_excel(file_path, header=None)
    return df


# selects date block out from initial dataframe; the date block is the subset of data with sequential dates in the
# left most column.
# column_index is the index of the column containing the right data. Needs to be manually input in the currency-specific
# functions.
# This function is the output function for this file.
def date_block_dataframe(file_path, column_index):
    if find_word(file_path, '.csv'):
        df = create_dataframe_from_csv(file_path)
    elif find_word(file_path, '.xls'):
        df = create_dataframe_from_xls(file_path)
    startend = get_indices_and_format((open_file_into_lists(file_path, column_index))[0])
    start = startend[0]
    end = startend[1]
    df_date_block_init = df[start:end]
    df_date_block = df_date_block_init.iloc[:, [0, column_index]]
    return df_date_block


# Returns lists containing the whole date column (unselected) and the whole of the column containing the desired data
# (also unselected). These lists will be used in determining the date format and start and end indices for the date
# block.
def open_file_into_lists(file_path, column_index):
    if find_word(file_path, '.csv'):
        df = create_dataframe_from_csv(file_path)
    elif find_word(file_path, '.xls'):
        df = create_dataframe_from_xls(file_path)
    dates_list = df.iloc[:, 0].values.tolist()
    data_list = df.iloc[:, column_index].values.tolist()

    return [dates_list, data_list]


# Sorts data according to data type: nan, bank holiday, data or miscellaneous.
def data_sorter(df):
    df_list = df.values.tolist()
    date_list = []
    data_list = []
    for a in range(len(df_list)):
        date_list.append((df_list[a])[0])
        data_list.append((df_list[a])[1])
    nan_index_list = []
    bank_holiday_index_list = []
    data_index_list = []
    misc_index_list = []
    for i, e in enumerate(data_list):
        if type(e) is not str:
            e = str(e)
        if bool(compile('\d').search(e)):
            data_index_list.append(i)
        elif e == 'nan':
            nan_index_list.append(i)
        elif e == ' Bank holiday':
            bank_holiday_index_list.append(i)
        else:
            misc_index_list.append(i)

    df_nan = DataFrame()
    df_bh = DataFrame()
    df_data_block = DataFrame()
    df_misc = DataFrame()

    list_index_list = [nan_index_list, bank_holiday_index_list, data_index_list, misc_index_list]
    list_dfs = [df_nan, df_bh, df_data_block, df_misc]

    for i, e in enumerate(list_index_list):
        if not len(e) == 0:
            for a in e:
                list_dfs[i] = list_dfs[i].append([df.iloc[a]])

    return list_dfs


# Categorises date formats.
def get_format(entry):
    try:
        entry.strftime('%Y-%m-%d')
        mem = 1
    except AttributeError:
        if type(entry) is not str:
            entry = str(entry)
        if find_word(entry, '[r]'):
            entry = delete_word(entry, '[r]')
        try:
            # entry = parser.parse(entry)
            try:
                datetime.strptime(entry, '%d/%m/%Y')
                entry = parser.parse(entry, dayfirst=True)
            except ValueError:
                entry = parser.parse(entry)
            mem = 1
        except ValueError:
            mem = 0
            pass

    return [entry, mem]


# Cuts off stuff top and bottom that aren't dates. Input is the raw dates.
def select_correct_dates(list_input):
    start_i = (get_indices_and_format(list_input))[0]
    end_i = (get_indices_and_format(list_input))[1]
    for i in range(len(list_input)):
        if i < start_i:
            list_input[i] = 'del'
        if i >= end_i:
            list_input[i] = 'del'
    list_input = list(filter(lambda aa: aa != 'del', list_input))
    return list_input


# Formats the dates. Input is the selected dates.
def format_selected_dates(list_input):
    dates_final = []
    for date in list_input:
        date_time = (get_format(date))[0]
        # dt = datetime.fromtimestamp(mktime(date_time))
        # date_final = dt.strftime('%Y-%m-%d') # delete this to keep dates as datetime things
        dates_final.append(date_time)
    return dates_final


# Changed to accept listed dataframe dates, returns order, indicating whether inversion is necessary.
def date_order(list_input2):
    order = ''
    if list_input2[0] < list_input2[1]:
        order = 'ascending'
    elif list_input2[0] > list_input2[1]:
        order = 'descending'
    return order


# Accepts same listed dataframe values as date_order and reorders dates if they're ascending.
def reorder(list_input3, necessary_or_not):
    reordered = []
    if necessary_or_not == 'ascending':
        for date in list_input3:
            reordered.insert(0, date)
    else:
        reordered = list_input3

    return reordered


# Gets start index and end index for date block and type of date for date block.
def get_indices_and_format(list_input1):
    start_index = 0
    end_index = 0
    memory = 0
    for i in range(len(list_input1) - 1):
        date_or_not = (get_format(list_input1[i]))[1] # corresponds to mem in get_format. 1 = date; 0 = not date
        date_or_not_next = (get_format(list_input1[i+1]))[1]
        if date_or_not == date_or_not_next and memory == 0 and not date_or_not == 0:
            start_index = i
            memory = 1
        if memory == 1 and not date_or_not == date_or_not_next:
            end_index = i+1
            break
        if memory == 1 and date_or_not == date_or_not_next and i == len(list_input1) - 2:
            end_index = i+2

    output_list = [start_index, end_index]
    return output_list


# Removes percentage signs from data.
def removes_percentage_signs(list_input4):
    list_output = []
    for dt in list_input4:
        if type(dt) is not str:
            dt = str(dt)
        if dt[-1] == '%':
            dt = dt[:-1]
        list_output.append(dt)
    return list_output


# Gives all data points to a set number of decimal places. Change the string to change the decimal places.
def limit_dp(list_input4):
    data_formatted = []
    for datum in list_input4:
        if type(datum) is not str:
            datum = str(datum)
        if bool(compile('\d').search(datum)):
            dt = Decimal(datum)
            dt_f = dt.quantize(Decimal(decimal_place_str), ROUND_HALF_UP)
        else:
            dt_f = datum
        data_formatted.append(dt_f)
    return data_formatted


# Checks if all the dates are descending. If not, the data are reordered.
def reordering_if_need_be(input_df1):
    df_list = input_df1.values.tolist()
    date_order_detection_list = [(df_list[0])[0], (df_list[1])[0]]
    second_parameter = date_order(date_order_detection_list)
    df_list_reordered = reorder(df_list, second_parameter)
    return df_list_reordered


# Splits the dates and data columns into separate lists. The function checks if the dataframe has only one value, since
# it would not only not need reordering, but the reordering sequence would not work on one value.
def df_list_into_lists(input_df2):
    df_list = input_df2.values.tolist()
    date_list = []
    data_list = []
    for entry in df_list:
        date_list.append(entry[0])
        data_list.append(entry[1])
    return[date_list, data_list]


def reordering(date_input, data_input):
    if len(date_input) > 1:
        decision = date_order([date_input[0], date_input[1]])
        reordered = reorder(list(zip(date_input, data_input)), decision)
    else:
        reordered = list(zip(date_input, data_input))
    return reordered


# Formats the date list.
def date_formatting(input_df3):
    date_init = (df_list_into_lists(input_df3))[0]
    date_output = format_selected_dates(date_init)
    return date_output


# Formats the data list.
def data_formatting(input_df4):
    data_init = (df_list_into_lists(input_df4))[1]
    data_output = (limit_dp(removes_percentage_signs(data_init)))
    return data_output


# Writes to a csv of specified name. The csv name is specified in the currency-specific scripts.
def csv_writing(input_df5, csv_name):
    date_input = date_formatting(input_df5)
    data_input = data_formatting(input_df5)
    tuple_output = reordering(date_input, data_input)
    with open(csv_name + '.csv', 'w') as csv_file:
        write = writer(csv_file)
        for tup in tuple_output:
            write.writerow(tup)


# Sorted dataframes are presented as a list of four dataframes, each with a different data type in it: nan, bank
# holiday, data and miscellaneous. output_func iterates through the list. If a dataframe has entries, those entries
# are formatted and written to a csv file.
# inherit_df = True if you want to pass a specific df to the func
# df_to_inherit specifies the df you want to be inherited
def output_func(file_name3, column_index, csv_name, inherit_df=False, df_to_inherit=None):
    files_made = []
    if inherit_df:
        date_input = date_formatting(df_to_inherit)
        data_input = data_formatting(df_to_inherit)
        with open(csv_name + '.csv', 'w') as csv_file:
            write = writer(csv_file)
            for x, y in zip(date_input, data_input):
                write.writerow([x, y])
    else:
        if find_word(file_name3, r'\\'):
            file_name1 = file_name3
        else:
            file_name1 = r'C:\\Users\\krish\\Downloads\\' + file_name3
        df = date_block_dataframe(file_name1, column_index)
        csv_seg_suffices = ['_nan', '_bh', '_data', '_misc']
        csv_seg_names = []
        for i in range(4):
            csv_seg_names.append(csv_name + csv_seg_suffices[i])
        data_seg = data_sorter(df)
        for i, e in enumerate(data_seg):
            if not e.empty:
                files_made.append(csv_seg_names[i])
                csv_writing(e, csv_seg_names[i])
        if path.exists(file_name1):
            remove(file_name1)
    return files_made


# Combines two formatted csvs (results of output_func) of all data types for a given currency. Used for aus, nzd
# Need to modify to ensure data in new csv file share the same number of decimal places.
def output2(file_names, column_index, csv_names, final_csv_name):
    files_made = []
    suffixes = ['nan', 'bh', 'data', 'misc']
    nan_files = []
    bh_files = []
    data_files = []
    misc_files = []
    names_files_made = [nan_files, bh_files, data_files, misc_files]
    for i, e in enumerate(file_names):
        for file in output_func(e, column_index, csv_names[i]):
            files_made.append(file)
    for file in files_made:
        for i, e in enumerate(suffixes):
            if find_word(file, e):
                names_files_made[i].append(file)

    for i, e in enumerate(names_files_made):
        if len(e) == 1:
            if path.exists(final_csv_name + '_' + suffixes[i] + '.csv'):
                remove(final_csv_name + '_' + suffixes[i] + '.csv')
            rename(e[0] + '.csv', final_csv_name + '_' + suffixes[i] + '.csv')
        elif len(e) > 1:
            join_csvs(e[0] + '.csv', e[1] + '.csv', final_csv_name + '_' + suffixes[i] + '.csv')
    for file in files_made:
        if path.exists(file):
            remove(file + '.csv')
