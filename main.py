import datetime
import requests
import time
from opc import OPC
from connect import Settings
from opcua import Client

print('Start App')

settings = Settings()

ip = settings.IP
api_key = settings.API_KEY
location = settings.LOCATION

url_get_data = f"http://{ip}/controller/data/logger/?location={location}&api_key={api_key}"
url_post_data = f'http://{ip}/data/add?api_key={api_key}'


def get_url(url):
    secure_response = requests.get(url)
    return secure_response.json()


def send_data(alldata):
    secure_response = requests.post(url_post_data, json=alldata)
    return secure_response.json()


def connect_and_create_inverters():
    try:
        create_data: dict = get_url(url_get_data)
        inverters = list()

        for connect in create_data.values():
            client = Client(f"opc.tcp://{connect['connect']['ip']}:{connect['connect']['port']}")

            for inv in connect['inv_reg']:
                inverters.append(OPC(client=client,
                                     serial_number=inv['serial_number'],
                                     read_dict=inv['registers']))
        return inverters
    except Exception as error:
        print(error)


inv_create = connect_and_create_inverters()


interval_minutes = 5
last_sent_data = {inv.serial_number: None for inv in
                  inv_create}  # Словарь для отслеживания последней отправленной информации

while True:
    try:
        data = list()
        current_time = datetime.datetime.now()
        if current_time.minute % interval_minutes == 0 and current_time.second == 0:

            for i in inv_create:
                reg = i.read_all_registers()
                if reg['inverter_registers_data']['current_power']['data'] == '0.00':
                    continue
                data.append(reg)

            # Проверка на одинаковые данные
            if all(last_sent_data.get(reg['serial_number']) == reg for reg in data):
                print("No new data to send.")
            else:
                date = datetime.datetime.now()
                print("send_data(data)", date, data)
                for reg in data:
                    last_sent_data[reg['serial_number']] = reg  # Обновляем отправленные данные

            time.sleep(60 - current_time.second)
        else:
            time.sleep(1)
    except Exception as e:
        print(e)
