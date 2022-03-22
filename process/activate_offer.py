import requests
import json
import uuid
import pandas as pd
from process.connect import make_api_request, get_token
from process.in_and_out import get_offer_data_file


def activate_offer(draft_id, token):
    new_command_id = str(uuid.uuid4())
    draft_activating_data = {
        "publication": {
            "action": "ACTIVATE"
        },
        "offerCriteria": [
            {
                "offers": [
                    {
                        "id": draft_id
                    }
                ],
                "type": "CONTAINS_OFFERS"
            }
        ]
    }
    draft_activating_data = json.dumps(draft_activating_data)
    activating_offer_url = f"https://api.allegro.pl/sale/offer-publication-commands/{new_command_id}"
    request_response = make_api_request(requests.put, activating_offer_url, data=draft_activating_data, token=token)

    return json.loads(request_response.text)


def deactivate_old_offer(offer_id, token):
    end_command_id = str(uuid.uuid4())
    deactivating_data = {
        "publication": {
            "action": "END"
        },
        "offerCriteria": [
            {
                "offers": [
                    {
                        "id": offer_id
                    }
                ],
                "type": "CONTAINS_OFFERS"
            }
        ]
    }
    deactivating_data = json.dumps(deactivating_data)
    deactivating_url = f"https://api.allegro.pl/sale/offer-publication-commands/{end_command_id}"
    request_response = make_api_request(requests.put, deactivating_url, data=deactivating_data, token=token)

    return json.loads(request_response.text)


def get_report(command_id, token):
    offer_response = make_api_request(
        func=requests.get,
        url=f"https://api.allegro.pl/sale/offer-publication-commands/{command_id}/tasks",
        token=token
    )
    return json.loads(offer_response.text)


def toggle_activity_offers_batch(offers_list, token, action="ACTIVATE"):

    offers_ids_array = [{'id': _id} for _id in offers_list]
    new_command_id = str(uuid.uuid4())
    action_data = {
        "publication": {
            "action": action
        },
        "offerCriteria": [
            {
                "offers": offers_ids_array,
                "type": "CONTAINS_OFFERS"
            }
        ]
    }
    action_data = json.dumps(action_data)
    activating_offer_url = f"https://api.allegro.pl/sale/offer-publication-commands/{new_command_id}"
    request_response = make_api_request(
        func=requests.put,
        url=activating_offer_url,
        data=action_data,
        token=token)
    return json.loads(request_response.text)


def end_all_offers():
    offers_data_file = get_offer_data_file()
    offer_data = pd.read_csv(offers_data_file, sep=';', encoding='UTF-8', low_memory=False)
    token = get_token()

    all_offer_ids = offer_data.offer_id.to_list()
    limit = 1000
    i = 0

    while i < len(all_offer_ids):
        offer_ids_batch = all_offer_ids[i:i + limit]
        batch_length = len(offer_ids_batch)
        # request_response = \
        toggle_activity_offers_batch(
            offers_list=offer_ids_batch,
            token=token,
            action="END")
        i += batch_length
        # print(request_response)
    print('Done!')


def ask_delete_offers():
    check = str(input("Dezaktywować oferty? (Y/N): ")).lower().strip()
    try:
        if check[0] == 'y':
            end_all_offers()
        elif check[0] == 'n':
            return None
        else:
            print('Niewłaściwa komenda')
            ask_delete_offers()
    except Exception as error:
        print("Coś poszło nie tak...")
        print(error)
        ask_delete_offers()

