import requests
import json
import csv
import os
import logging
from datetime import datetime
from process.setup import DATETIME_FORMAT
from process.connect import get_token, make_api_request


def get_csv_writer(column_names):
    root_path = os.path.dirname(os.environ.get('APP_ROOT'))
    account_name = os.environ.get('account_name')
    now = datetime.now()
    now_date_str = now.strftime(DATETIME_FORMAT)
    csv_file_path = os.path.join(root_path, 'output', f'{now_date_str}__{account_name}__offers_data.csv')
    csv_file = open(csv_file_path, "w", encoding='utf-8', newline='')
    writer = csv.DictWriter(csv_file, fieldnames=column_names, delimiter=';')
    writer.writeheader()
    return writer


def get_total_amount(token):
    total_amount_data = {
        "publication.status": "ACTIVE",
        "sort": "-stock.sold",
        "limit": 1}
    total_amount_response = make_api_request(
        func=requests.get,
        url="https://api.allegro.pl/sale/offers",
        data=total_amount_data,
        token=token)
    total_offers = json.loads(total_amount_response.text)
    return total_offers['totalCount']


def get_own_listing_offers(account_token):
    url = f'https://api.allegro.pl/sale/offers'

    limit = 1000
    total_count = 1
    count = 0
    all_offers = []

    test_your_limits = 10**6

    while count < total_count and count < test_your_limits:
        browse_params = {
            "sort": "-stock.sold",
            "limit": min(limit, test_your_limits),
            "offset": count}

        offers_response = make_api_request(requests.get, url, account_token, browse_params)
        offers_data = json.loads(offers_response.text)

        total_count = offers_data['totalCount']
        batch_count = offers_data['count']
        all_offers += offers_data['offers']
        count += batch_count

    return all_offers


def get_offer_details(offer_id, token):
    offer_response = make_api_request(
        func=requests.get,
        url=f"https://api.allegro.pl/sale/offers/{offer_id}",
        token=token)

    return json.loads(offer_response.text)


def check_account_offers():
    token = get_token()
    offers = get_own_listing_offers(account_token=token)

    check_offer_cols = ['sku', 'offer_id', 'price', 'stock', 'publication', 'check']

    csv_data_writer = get_csv_writer(column_names=check_offer_cols)

    for offer in offers:
        if offer['external'] is None:
            logging.info('no sku in offer id', offer['id'])
            pass
        else:
            offer_values = {
                'sku': offer['external']['id'],
                'offer_id': offer['id'],
                'price': offer['sellingMode']['price']['amount'],
                'stock': offer['stock']['available'],
                'publication': offer['publication']['status'],
                'check': False
            }

            csv_data_writer.writerow(offer_values)


if __name__ == "__main__":
    pass
