import os
import logging
from datetime import datetime, timedelta
from process.check_own_offers import check_account_offers
from process.setup import DATETIME_FORMAT


def get_file_create_datetime(file):
    time_string = str(os.path.basename(file)).split('__')[0]
    file_create_datetime = datetime.strptime(time_string, DATETIME_FORMAT)

    return file_create_datetime


def get_latest_file(file_folder, account_name):
    input_files = [os.path.join(file_folder, file) for file in os.listdir(file_folder) if f'_{account_name}_' in file]
    if input_files:
        input_files = sorted(input_files, key=lambda x: get_file_create_datetime(x))
        file = input_files[-1]
    else:
        file = None
    return file


def get_offer_data_file():
    root_path = os.path.dirname(os.environ.get('APP_ROOT'))
    account_name = os.environ.get('account_name')
    file_folder = os.path.join(root_path, 'output')
    logging.debug(f'Szukam pliku z ofertami {account_name} w {file_folder}')

    file = get_latest_file(file_folder, account_name)

    if not file:
        check_account_offers()
        file = get_offer_data_file()

    file_age = datetime.now() - get_file_create_datetime(file)
    if file_age > timedelta(hours=24):
        logging.info('Plik starszy niż 24h. Pobieranie aktualnych danych o ofertach')
        check_account_offers()
        file = get_offer_data_file()

    return file


def get_input_data():
    root_path = os.path.dirname(os.environ.get('APP_ROOT'))
    file_folder = os.path.join(root_path, 'input')
    input_files = [os.path.join(file_folder, file) for file in os.listdir(file_folder)]
    input_files = sorted(input_files, key=lambda x: os.path.getmtime(x))
    file = input_files[-1]

    return file
