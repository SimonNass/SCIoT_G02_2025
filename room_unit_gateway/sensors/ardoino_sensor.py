import logging
logger = logging.getLogger(__name__)

from sensors.sensor import SensorInterface
from enumdef import Connectortype, Notifyinterval
from networking.ardoino_reverse_proxy import ArdoinoReverseProxy


class ArdoinoSensor(SensorInterface):
    def __init__(self, name: str, type_name: str, connector: int, connector_types: Connectortype, min_value: int, max_value: int, datatype: str, unit: str, read_interval: int, notify_interval: Notifyinterval, notify_change_precision: int, ardoino_serial: ArdoinoReverseProxy, type_name_ardoino: str):
        if connector_types != Connectortype.Analog:
            raise ValueError("Connector_type is not Analog.")
        super().__init__(name=name, type_name=type_name, connector=connector, connector_types=connector_types, min_value=min_value, max_value=max_value, datatype=datatype, unit=unit, read_interval=read_interval, notify_interval=notify_interval, notify_change_precision=notify_change_precision)
        self.type_name_ardoino = type_name_ardoino
        # in bps
        self.ardoino_serial = ardoino_serial
        _ = self.read_sensor()

    def __del__(self):
        try:
            self.ardoino_serial.close()
        except (Exception, IOError, TypeError, AttributeError) as e:
            print ("closing ardoino_serial was unsucesful")
            #print (e)
            logger.info("closing ardoino_serial was unsucesful {}".format(e))

    def read_internal_sensor(self):
        self.ardoino_serial.remote_call(self.type_name_ardoino, 0)
        return 0

