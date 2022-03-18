import dotenv
import os

DATETIME_FORMAT = '%Y-%m-%d_%H%M'


def setup():
    root_path = os.environ.get('APP_ROOT')
    dotenv_path = os.path.join(root_path, '.env')
    dotenv_file = dotenv.find_dotenv(dotenv_path)

    current_tolerance_value = os.environ['difference_tolerance_%']
    difference_tolerance = input(f'Tolerancja różnicy ceny % ({current_tolerance_value}) ') or current_tolerance_value
    dotenv.set_key(dotenv_file, 'difference_tolerance_%', difference_tolerance)

    current_price_modifier = os.environ['price_modifier_%']
    price_modifier = input(f'Modyfikator ceny % ({current_price_modifier}) ') or current_price_modifier
    dotenv.set_key(dotenv_file, 'price_modifier_%', price_modifier)

    current_name = os.environ['account_name']
    account_name = input(f'Nazwa ({current_name}) ') or current_name
    dotenv.set_key(dotenv_file, 'account_name', account_name)
