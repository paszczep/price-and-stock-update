import csv
import os
from datetime import datetime


def get_csv_writer(column_names):
    root_path = os.path.dirname(os.environ.get('APP_ROOT'))
    account_name = os.environ.get('account_name')
    now = datetime.now()
    now_date_str = now.strftime('%Y-%m-%d')
    csv_file_path = os.path.join(root_path, 'output', f'{now_date_str}__{account_name}__offers_data.csv')
    csv_file = open(csv_file_path, "w", encoding='utf-8', newline='')
    writer = csv.DictWriter(csv_file, fieldnames=column_names, delimiter=';')
    writer.writeheader()
    return writer


def get_data_input(dir_name):
    root_path = os.path.dirname(os.environ.get('APP_ROOT'))
    account_name = os.environ.get('account_name')
    file_folder = os.path.join(root_path, dir_name)
    if dir_name == 'output':
        input_files = [os.path.join(file_folder, file) for file in os.listdir(file_folder) if f'_{account_name}_' in file]
    else:
        input_files = [os.path.join(file_folder, file) for file in os.listdir(file_folder)]
    input_files = sorted(input_files, key=lambda x: os.path.getmtime(x))
    file = input_files[-1]

    return file


if __name__ == "__main__":
    print(get_data_input(dir_name='output'))
