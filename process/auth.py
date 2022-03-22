import requests
import base64
import json
import os
import dotenv
from datetime import datetime


def run_auth_2():
    client_id = str.encode(os.environ.get('CLIENT_ID'))
    client_secret = str.encode(os.environ.get('CLIENT_SECRET'))
    device_code = os.environ.get('DEVICE_CODE')

    authorization_encode = base64.b64encode(client_id + b":" + client_secret)
    url = f"https://allegro.pl/auth/oauth/token" \
          f"?grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Adevice_code&device_code={device_code}"
    authorization = b"Basic " + authorization_encode
    headers = {"Authorization": authorization}

    auth_response = requests.post(url, headers=headers)

    if auth_response.status_code != 200:
        raise Exception(f"Błąd autoryzacji. "
                        f"Kod statusu {auth_response.status_code}. "
                        f"Powód {auth_response.reason}")

    new_token = json.loads(auth_response.text)
    new_token_json = {
                "token": new_token['access_token'],
                "refresh_token": new_token['refresh_token'],
                "refresh_date": datetime.now().strftime("%Y-%m-%dT%H:%M")
            }

    app_root = os.environ.get('APP_ROOT')

    token_file_path = os.path.join(app_root, 'token.json')

    with open(token_file_path, "w") as token_file:
        token_file.write(json.dumps(new_token_json))


def run_auth_1():

    client_id = str.encode(os.environ.get('CLIENT_ID'))
    client_secret = str.encode(os.environ.get('CLIENT_SECRET'))

    authorization_encode = base64.b64encode(client_id + b":" + client_secret)
    url = "https://allegro.pl/auth/oauth/device"
    authorization = b"Basic " + authorization_encode
    headers = {"Authorization": authorization}
    device_data = {
        "client_id": client_id,
    }

    auth_response = requests.post(url, headers=headers, data=device_data)
    if auth_response.status_code != 200:
        raise Exception(f"{auth_response.status_code} - {auth_response.reason}")

    new_token = json.loads(auth_response.text)

    print('Autoryzuj proces na ', new_token['verification_uri_complete'])

    device_code_key = 'DEVICE_CODE'

    os.environ[device_code_key] = new_token['device_code']

    dotenv_path = os.path.join(os.environ.get('APP_ROOT'), '.env')
    dotenv_file = dotenv.find_dotenv(dotenv_path)
    dotenv.set_key(dotenv_file, device_code_key, os.environ[device_code_key])

    return new_token['device_code']


def run_auth():
    run_auth_1()
    input('Wciśnij Enter...')
    run_auth_2()
    print('Autoryzacja zakończona')


