import requests
import json
import os.path
import base64
import logging
from datetime import datetime, timedelta


def make_api_request(func, url, token, data=None):
    accept = "application/vnd.allegro.public.v1+json"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": accept
    }
    resp = func(url, headers=headers, data=data, timeout=10)
    resp.encoding = 'utf-8'

    if resp.status_code not in [200, 201]:
        warning_str = f"{resp.status_code} - {resp.reason}."
        logging.warning(warning_str)
        raise Exception

    return resp


def make_api_request_offer(func, url, token, data=None):
    accept = "application/vnd.allegro.public.v1+json"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": accept
    }
    resp = func(url, headers=headers, data=data, timeout=10)
    resp.encoding = 'utf-8'

    if resp.status_code not in [200, 201]:
        warning_str = f"{resp.status_code} - {resp.reason} - {json.loads(resp.text)['errors'].pop()['message']}."
        logging.warning(warning_str)
        raise Exception

    return resp


def get_token():
    app_root = os.environ.get('APP_ROOT')
    token_file_path = os.path.join(app_root, 'token.json')

    if not os.path.isfile(token_file_path):
        warning_str = f"Brak pliku z danymi do utworzenia tokena {token_file_path}"
        print(warning_str)
        logging.warning(warning_str)
        raise Exception

    with open(token_file_path, "r") as token_file:
        token_json = json.loads(token_file.read())

    token_date = datetime.strptime(token_json['refresh_date'], '%Y-%m-%dT%H:%M')
    token_date_expired = (datetime.now() - token_date) > timedelta(hours=12)

    if token_date_expired:
        client_id = str.encode(os.environ.get('CLIENT_ID'))
        client_secret = str.encode(os.environ.get('CLIENT_SECRET'))

        authorization_encode = base64.b64encode(client_id + b":" + client_secret)
        url = "https://allegro.pl/auth/oauth/token"
        authorization = b"Basic " + authorization_encode
        headers = {"Authorization": authorization}
        refresh_data = {
            "grant_type": "refresh_token",
            "refresh_token": token_json['refresh_token']
        }
        refresh_response = requests.post(url, headers=headers, data=refresh_data)

        if refresh_response.status_code != 200:
            problem_str = f"Kod statusu {refresh_response.status_code} - {refresh_response.reason}"
            logging.warning(problem_str)
            print(problem_str)
            raise Exception
        new_token = json.loads(refresh_response.text)
        new_token_json = {
            "token": new_token['access_token'],
            "refresh_token": new_token['refresh_token'],
            "refresh_date": datetime.now().strftime("%Y-%m-%dT%H:%M")
        }
        with open(token_file_path, "w") as token_file:
            token_file.write(json.dumps(new_token_json))
        return new_token['access_token']
    else:
        return token_json['token']
