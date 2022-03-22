import os.path
import dotenv
import time
import sys
import logging
from datetime import datetime, timedelta

sys.path.append('..')
from process.setup import setup
from process.auth import run_auth
from process.edit_offer import update_offers
from process.activate_offer import ask_delete_offers
from process.check_own_offers import check_account_offers


logger = logging.getLogger(__name__)

logging.basicConfig(filename='log.csv', level=logging.INFO, format='%(asctime)s; %(levelname)s ; %(message)s')

dotenv_file = dotenv.find_dotenv()
os.environ['APP_ROOT'] = os.path.dirname(os.path.realpath(__file__))
dotenv.set_key(dotenv_file, 'APP_ROOT', os.environ['APP_ROOT'])
dotenv.load_dotenv(dotenv_file)


def run_help():
    print("'auth' - autoryzacja",
          "'auto' - 'check' -> 'update'",
          "'check' - pobierz aktualne parametry ofert autoryzowanego konta",
          "'update' - aktualizuj stany magazynowe i ceny ofert",
          "'setup' - wprowadzanie parametrów aktualizacji",
          "'end' - zakończ wszystkie oferty na autoryzowanym koncie",
          sep='\n')


def run_auto():
    logging.info('Start')
    start_time = datetime.now()
    update_offers()
    end_time = datetime.now()
    delta_time = end_time - start_time
    logging.info(f'Czas trwania: {str(delta_time)}')
    sleep_time_hrs = 11
    logging.info(f'Czekam do {datetime.now() + timedelta(hours=sleep_time_hrs)}.')
    time.sleep(sleep_time_hrs * 60 ** 2)
    run_auto()


PROCESS_MAP = {
    'auth': run_auth,
    'auto': run_auto,
    'check': check_account_offers,
    'update': update_offers,
    'setup': setup,
    'end': ask_delete_offers,
    'help': run_help,
}


def try_except(given_command):
    try:
        PROCESS_MAP[given_command]()
    except Exception as ex:
        logging.warning(ex)
        time.sleep(10*60)  # 10 minut
        try_except(given_command)


def run_from_command_line(command):
    if command in PROCESS_MAP.keys():
        try_except(command)
    else:
        print('Błędna komenda')
        run_help()


def run_menu():
    commands = list(PROCESS_MAP.keys()) + ['exit']
    for com in commands:
        print(com)

    while True:
        command = input('Command: ')
        if command in PROCESS_MAP.keys():
            try_except(command)
        elif command in ['exit', 'x', 'X']:
            break
        elif command in [' ', '']:
            continue
        else:
            print('Błędna komenda')
            continue


if __name__ == "__main__":

    command_args = sys.argv

    if len(command_args) == 1:
        run_menu()
    elif len(command_args) == 2:
        run_from_command_line(command_args[1])
    else:
        print('Niewłaściwe argumenty')
