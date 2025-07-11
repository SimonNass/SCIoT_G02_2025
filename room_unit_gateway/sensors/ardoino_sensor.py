"""Module specifies the sensors on the arduino."""

from sensors.sensor import SensorInterface
from enumdef import Connectortype, Notifyinterval
from networking.ardoino_reverse_proxy import ArdoinoReverseProxy

import logging
logger = logging.getLogger(__name__)

class ArdoinoSensor(SensorInterface):
    def __init__(self, name: str, type_name: str, connector: int, connector_types: Connectortype, min_value: int, max_value: int, datatype: str, unit: str, read_interval: int, notify_interval: Notifyinterval, notify_change_precision: int, ardoino_serial: ArdoinoReverseProxy, type_name_ardoino: str):
        #if connector_types != Connectortype.Analog:
        #    raise ValueError("Connector_type is not Analog.")
        super().__init__(name=name, type_name=type_name, connector=connector, connector_types=connector_types, min_value=min_value, max_value=max_value, datatype=datatype, unit=unit, read_interval=read_interval, notify_interval=notify_interval, notify_change_precision=notify_change_precision)
        self.type_name_ardoino = type_name_ardoino
        # in bps
        self.ardoino_serial = ardoino_serial
        _ = self.read_sensor()

    def read_internal_sensor(self):
        value = self.ardoino_serial.remote_call(self.type_name_ardoino, 0)
        return value
