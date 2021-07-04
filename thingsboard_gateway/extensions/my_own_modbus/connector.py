import random
import time
from threading import Thread
from typing import Optional

from pymodbus.client.sync import ModbusTcpClient
from pymodbus.exceptions import ConnectionException, ModbusIOException
from pymodbus.register_read_message import ReadInputRegistersResponse

from thingsboard_gateway import TBGatewayService
from thingsboard_gateway.connectors.connector import Connector, log
from thingsboard_gateway.tb_utility.tb_loader import TBModuleLoader


class MyOwnModbusConnector(Thread, Connector):
    def __init__(self, gateway: TBGatewayService, config: dict, connector_type: str):
        super().__init__()
        self.__gateway = gateway
        self.__config = config
        self.__connector_type = connector_type

        self.statistics = {'MessagesReceived': 0,
                           'MessagesSent': 0}

        self.setName(config.get('name', self.name))

        self.daemon = True
        self.__is_active = False

        self.__poll_interval = self.__config.get('poll_interval', 1)
        self.__unit = self.__config.get('unit', 1)
        converter_class_name = self.__config.get('converter_class_name')
        assert converter_class_name is not None
        converter_class = TBModuleLoader.import_module(connector_type, converter_class_name)
        self.__converter_instance = converter_class()

        ip_addr = self.__config.get('ip_addr', '127.0.0.1')
        port = self.__config.get('port', 5440)
        self.__modbus_client = ModbusTcpClient(ip_addr, port=port)

    def open(self):
        self.__is_active = True
        self.__modbus_client.connect()
        self.start()

    def __reconnect(self):
        log.info('trying to reestablish connection')
        self.__modbus_client.connect()

    def close(self):
        self.__is_active = False
        self.__modbus_client.close()

    def get_name(self):
        return self.name

    def is_connected(self):
        return self.__is_active

    def on_attributes_update(self, content):
        print('on_attributes_update')

    def server_side_rpc_handler(self, content):
        print('server_side_rpc_handler')

    def run(self):
        try:
            while self.__is_active:
                registers_response: Optional[ReadInputRegistersResponse] = None
                try:
                    rr: Optional[ReadInputRegistersResponse, ModbusIOException] = self.__modbus_client.read_input_registers(0, 2, unit=self.__unit)
                    if not isinstance(rr, ModbusIOException):
                        registers_response = rr
                except ModbusIOException as e:
                    self.__reconnect()
                    log.exception(e)
                except ConnectionException as e:
                    self.__reconnect()
                    log.exception(e)
                except Exception as e:
                    log.exception(e)
                    # raise e
                if registers_response is not None:
                    try:
                        converted_data = self.__converter_instance.convert(self.__config, registers_response)
                        self.__gateway.send_to_storage(self.get_name(), converted_data)
                    except Exception as e:
                        log.exception(e)
                time.sleep(self.__poll_interval)
        except Exception as e:
            log.exception(e)

