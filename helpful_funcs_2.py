from datetime import datetime
from datetime import date
from pandas import read_csv
from pandas import concat
from os import path
from csv import reader
from collections import defaultdict
from helpful_funcs import find_word
from date_block_selector import date_block_dataframe
from data_sorter import data_seg_func
from formatter_and_output import output_func


# if, for a 'historical' data file there is a df with new data of the same type, this works to join the two data sets
# and process them together. If there is no new df, it doesn't exist in data_seg_func(df_input)
# and so won't lead to the program.
def join_hist_with_pres(file_name, column_index, csv_names, old_data_file_name, download_path,
                        inherit_df=False, df_inherited=None):
    now = datetime.now()
    current_year = now.year
    current_month = now.month
    current_day = now.day
    past_year = current_year - 10
    past_date = date(past_year, current_month, current_day).isoformat()
    if inherit_df:
        df_input = df_inherited
    else:
        if find_word(file_name, r'\\'):
            file_name1 = file_name
        else:
            file_name1 = r'C:\\Users\\krish\\Downloads\\' + file_name
        df_input = date_block_dataframe(file_name1, 1)
    for i, e in enumerate(data_seg_func(df_input)):
        csv_seg_suffices = ['_nan', '_bh', '_data', '_misc']
        old_data_file_path = old_data_file_name + csv_seg_suffices[i] + '.csv'
        if path.exists(old_data_file_path):
            df_old = read_csv(old_data_file_path, encoding='cp1252', header=None)
            dates_old = df_old.iloc[:, 0].values.tolist()
            start_idx_hist = 0
            for idx, entry in enumerate(dates_old):
                if type(entry) is not str:
                    entry = str(entry)
                if entry < past_date:
                    start_idx_hist = idx
                    break

            df_selected_old = df_old.iloc[start_idx_hist:, [0, column_index]]
            df_new = e
            df_new.columns = [0, 1]
            df_joined = concat([df_new, df_selected_old])

            csv_name = csv_names + csv_seg_suffices[i]

            output_func(file_name, 1, csv_name, inherit_df=True, df_to_inherit=df_joined)


# csv_file is jpn_gen in this case. Returns first five tups on file. Need only get data on val_dates and then check the
# past dates and data match up
def pull_validation(csv_file):
    columns = defaultdict(list)
    with open(csv_file) as f:
        read = reader(f)
        for row in read:
            for (i, v) in enumerate(row):
                columns[i].append(v)
    dates = columns[0]
    data = columns[1]
    val_dates = dates[:5]
    val_data = data[:5]
    return list(zip(val_dates, val_data))


# Checks incoming data against old validation data. If all is well, new data is returned, to be added to existing data.
def validate(incoming_tuples, validation_tuples):
    check_list = incoming_tuples[-5:]
    mismatch_list = [item for item in check_list if item not in validation_tuples]
    if len(mismatch_list) != 0:
        print('Data mismatch')
        for mismatch in mismatch_list:
            print('Mismatch at:' + str(mismatch[0]))
    else:
        print('Data match')
        new_tuples = [item for item in incoming_tuples if item not in validation_tuples]
        return new_tuples
