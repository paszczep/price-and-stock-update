import requests
import json
from process.connect import get_token, make_api_request
from process.in_and_out import get_csv_writer


def get_total_amount():
    total_amount_data = {
        "publication.status": "ACTIVE",
        "sort": "-stock.sold",
        "limit": 1
    }
    total_amount_response = make_api_request(requests.get, "https://api.allegro.pl/sale/offers", total_amount_data)
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
        print(f'{len(all_offers)} / {total_count}')

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
            print('no sku in offer id', offer['id'])
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
