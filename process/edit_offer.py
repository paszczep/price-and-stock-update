import pandas as pd
import requests
import json
import logging
from process.connect import make_api_request, get_token
from process.get_update_data import get_offer_price_and_stock_data
from process.activate_offer import deactivate_old_offer, activate_offer
from process.in_and_out import get_offer_data_file
from process.check_own_offers import get_total_amount


def put_offer_on_sale(offer_id, offer_data, token):

    offer_response = make_api_request(
        func=requests.put,
        url=f"https://api.allegro.pl/sale/offers/{offer_id}",
        token=token,
        data=offer_data)
    return json.loads(offer_response.text)['id']


def get_offer_details(offer_id, token):

    offer_response = make_api_request(
        func=requests.get,
        url=f"https://api.allegro.pl/sale/offers/{offer_id}",
        token=token)

    return json.loads(offer_response.text)


def get_offers_to_update_by_ids(offer_ids_list: list, token):

    offers = []

    for offer_id in offer_ids_list:
        try:
            offer_details = get_offer_details(offer_id=offer_id, token=token)
            offers.append(offer_details)
        except Exception as ex:
            logging.warning(ex)

    return offers


def edit_particular_offer(offer_edit, update_data):
    ofr_id = int(offer_edit['id'])
    update_data_row = update_data.loc[update_data.offer_id == ofr_id]
    new_brutto_price = "{0:.2f}".format(round(update_data_row['Cena sprzedaży brutto'].values[0], 2))
    new_stock = int(update_data_row['Stan magazynowy'].values[0]) or 0
    offer_edit['sellingMode']['price']['amount'] = new_brutto_price
    offer_edit['stock']['available'] = new_stock

    for key in offer_edit['promotion'].keys():
        offer_edit['promotion'][key] = False

    return offer_edit


def update_offers():
    token = get_token()
    total_active_offers = get_total_amount(token)
    logging.info(f'Aktywnych ofert na koncie: {total_active_offers}')
    check_offer_data_file = get_offer_data_file()
    check_offer_data = pd.read_csv(check_offer_data_file, sep=';', encoding='UTF-8', low_memory=False)

    update_data = pd.DataFrame(get_offer_price_and_stock_data())
    offer_ids_large_list = update_data.offer_id.to_list()
    offers_list_length = len(offer_ids_large_list)

    batch_size = 10
    list_of_lists = [offer_ids_large_list[i:i + batch_size] for i in range(0, offers_list_length, batch_size)]

    for offer_ids_list in list_of_lists:

        got_offers = get_offers_to_update_by_ids(offer_ids_list, token)

        for offer_edit in got_offers:
            ofr_id = offer_edit['id']

            try:
                offer_edit = edit_particular_offer(offer_edit, update_data)
                if offer_edit['stock']['available'] == 0:
                    logging.info(f"Koniec {ofr_id}")
                    deactivate_old_offer(offer_id=ofr_id, token=token)
                    check_offer_data.loc[check_offer_data.offer_id == int(ofr_id), 'check'] = True

                else:
                    offer_edit_encoded = json.dumps(offer_edit).encode("UTF-8")
                    returned_offer_id = put_offer_on_sale(offer_id=ofr_id, offer_data=offer_edit_encoded, token=token)
                    logging.info(f'"ok" {returned_offer_id}')
                    if offer_edit['stock']['available'] > 0 and offer_edit['publication']['status'] == "ENDED":
                        logging.info(f"Aktywacja {returned_offer_id}")
                        activate_offer(returned_offer_id, token)
                    check_offer_data.loc[check_offer_data.offer_id == int(returned_offer_id), 'check'] = True

            except Exception as exception:
                logging.warning(f'Błąd oferty {ofr_id} - {exception}')
                # for key, value in offer_edit.items():
                #     if key in ['id', 'name', 'sellingMode', 'stock', 'external']:
                #         print(key, value)
                check_offer_data.loc[check_offer_data.offer_id == int(ofr_id), 'check'] = True

            check_offer_data.to_csv(check_offer_data_file, encoding='UTF-8', sep=';', index=False)


# if __name__ == "__main__":
#
#     update_offers()
