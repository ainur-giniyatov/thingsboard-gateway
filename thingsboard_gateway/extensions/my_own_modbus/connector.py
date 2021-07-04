import random
import time
from threading import Thread

from thingsboard_gateway import TBGatewayService
from thingsboard_gateway.connectors.connector import Connector, log


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

    def open(self):
        self.__is_active = True
        self.start()

    def close(self):
        self.__is_active = False

    def get_name(self):
        return self.name

    def is_connected(self):
        return True

    def on_attributes_update(self, content):
        pass

    def server_side_rpc_handler(self, content):
        pass

    def run(self):
        while self.__is_active:
            time.sleep(1)
            print('polling data')
            data = {
                "deviceName": "device 1",
                "deviceType": "unknown",
                "attributes": [
                                {"attr1": "good"},
                                {"attr2": False}
                              ],
                "telemetry": [
                                {"val1": random.random() * 10.0},
                                {"val2": random.randint(-40, 130)},
                              ]
            }
            self.__gateway.send_to_storage(self.get_name(), data)

