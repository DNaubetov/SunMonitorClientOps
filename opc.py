from decimal import Decimal
from opcua import Client


class OPC:
    def __init__(self, client: Client, serial_number, read_dict: dict):
        self.client = client
        self.serial_number = serial_number
        self.registers_dict = read_dict

    def read_registers(self, name: str):
        try:
            register: bool | dict = self.registers_dict.get(name, False)
            if register is False:
                return
            data = self.client.get_node(register['registers']).get_value()

            if register.get('coefficient', False):
                return {'data': str(round(Decimal(str(data)) * Decimal(register["coefficient"]), 2)),
                        'unit': register["unit"]}

            return {'data': str(data)}
        except Exception as e:
            return e

    def read_all_registers(self):
        try:
            self.client.connect()
            reg = {name: self.read_registers(name) for name in self.registers_dict.keys()}
            data = {'serial_number': self.serial_number, "inverter_registers_data": reg}
            return data
        except Exception as error:
            print('End', error)
        finally:
            self.client.disconnect()
