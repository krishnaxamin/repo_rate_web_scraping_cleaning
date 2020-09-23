from csv import reader
from csv import writer
from collections import defaultdict
from os import path
from os import remove

""" Contains functions useful across the board but not necessarily belonging to specific pathways."""


# Joins two complete csvs together. Checks for shared data and ensures no duplication.
# Modify so that data share same number of decimal places. --> should be unnecessary since everything is to 5dp
def join_csvs(csv1, csv2, csv3):
    columns1 = defaultdict(list)
    with open(csv1) as f1:
        read = reader(f1)
        for row in read:
            for (i, v) in enumerate(row):
                columns1[i].append(v)
    dates1 = columns1[0]
    data1 = columns1[1]
    list1 = list(zip(dates1, data1))
    columns2 = defaultdict(list)
    with open(csv2) as f2:
        read2 = reader(f2)
        for row2 in read2:
            for (i, v) in enumerate(row2):
                columns2[i].append(v)
    dates2 = columns2[0]
    data2 = columns2[1]
    list2 = list(zip(dates2, data2))
    final_list = csv_overlap(list1, list2)
    dates_final = []
    data_final = []
    for tup in final_list:
        dates_final.append(tup[0])
        data_final.append(tup[1])
    if path.exists(csv1):
        remove(csv1)
    if path.exists(csv2):
        remove(csv2)
    with open(csv3, 'w') as f3:
        write = writer(f3)
        for x, y in zip(dates_final, data_final):
            write.writerow([x, y])


# checks for overlap between joining csvs and removes the overlap from the latter i.e. csv2 not csv1. Inputs lists
# from both csvs.
def csv_overlap(list_input1, list_input2):
    input_2_cut = [item for item in list_input2 if item not in list_input1]
    for entry in input_2_cut:
        list_input1.append(entry)
    return list_input1


# Basically the .find function but made to return a bool.
def find_word(string, sub_str):
    if string.find(sub_str) == -1:
        output = False
    else:
        output = True

    return output


# Equalises the rows in a csv file so it can be opened into a dataframe. Such a function is not necessary for Excel
# files.
def equalise_rows(file_path):
    with open(file_path) as f:
        read = reader(f)
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

    with open(file_path, 'w') as f1:
        write = writer(f1)
        for a in row_list:
            write.writerow(a)


# Returns a string with the sub_str deleted
def delete_word(string, sub_str):
    output = ''
    start_i = string.find(sub_str)
    end_i = string.find(sub_str[-1]) + 1
    if start_i != 0 and end_i < len(string):
        output = string[:start_i] + string[end_i:]
    if start_i != 0 and end_i == len(string):
        output = string[:start_i]
    if start_i == 0 and end_i < len(string):
        output = string[end_i:]
    return output


def add_data_to_csv(csv_file, input_data, new_csv_file):
    columns = defaultdict(list)
    with open(csv_file) as f:
        read = reader(f)
        for row in read:
            for (i, v) in enumerate(row):
                columns[i].append(v)
    csv_dates = columns[0]
    csv_data = columns[1]
    csv_zip_list = list(zip(csv_dates, csv_data))
    new_data_list = input_data + csv_zip_list
    with open(new_csv_file, 'w') as f1:
        write = writer(f1)
        for tup in new_data_list:
            write.writerow(tup)
