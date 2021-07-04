from thingsboard_gateway.connectors.converter import Converter


class MyOwnUpConverter(Converter):
    def __init__(self):
        super().__init__()

    def convert(self, config: dict, raw_data):
        converted_data = {
            "deviceName": "device 1",
            "deviceType": "unknown",
            "attributes": [
                {"attr1": "good"},
                {"attr2": False}
            ],
            "telemetry": [
                {"val1": raw_data.registers[0]},
                {"val2": raw_data.registers[1]},
            ]
        }
        return converted_data
