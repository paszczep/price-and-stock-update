import os
from datetime import datetime, timedelta
from process.check_own_offers import check_account_offers
from process.setup import DATETIME_FORMAT


def get_offer_data_file():
    root_path = os.path.dirname(os.environ.get('APP_ROOT'))
    account_name = os.environ.get('account_name')
    file_folder = os.path.join(root_path, 'output')
    input_files = [os.path.join(file_folder, file) for file in os.listdir(file_folder) if f'_{account_name}_' in file]
    input_files = sorted(input_files, key=lambda x: os.path.getmtime(x))
    file = input_files[-1]
    time_string = str(os.path.basename(file)).split('__')[0]
    file_age = datetime.now() - datetime.strptime(time_string, DATETIME_FORMAT)

    if file_age > timedelta(hours=24):
        check_account_offers()
        get_offer_data_file()

    return file


def get_input_data():
    root_path = os.path.dirname(os.environ.get('APP_ROOT'))
    file_folder = os.path.join(root_path, 'input')
    input_files = [os.path.join(file_folder, file) for file in os.listdir(file_folder)]
    input_files = sorted(input_files, key=lambda x: os.path.getmtime(x))
    file = input_files[-1]

    return file


if __name__ == "__main__":
    print(get_input_data())
