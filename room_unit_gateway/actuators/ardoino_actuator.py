import time
import logging
logger = logging.getLogger(__name__)

from actuators.actuator import ActuatorInterface
from enumdef import Connectortype
from networking.ardoino_reverse_proxy import ArdoinoReverseProxy

class ArdoinoActuator(ActuatorInterface):
    def __init__(self, name: str, type_name: str, connector: int, connector_types: Connectortype, min_value: int, max_value: int, datatype: str, unit: str, initial_value: int, off_value: int, message_end_signal: str, usb_channel_type: str, usb_channel_data_rate: int):
        if connector_types != Connectortype.Analog:
            raise ValueError("Connector_type is not Analog.")
        super().__init__(name=name,type_name=type_name,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value,datatype=datatype,unit=unit,initial_value=initial_value,off_value=off_value)
        self.type_name = "motor"
        # in bps
        self.ardoino_serial = ArdoinoReverseProxy(message_end_signal=message_end_signal,usb_channel_type=usb_channel_type,usb_channel_data_rate=usb_channel_data_rate)
        time.sleep(2)
        self.write_actuator(self.initial_value)

    def __del__(self):
        try:
            del self.ardoino_serial
        except (Exception, IOError, TypeError, AttributeError) as e:
            print ("closing ardoino_serial was unsucesful")
            #print (e)
            logger.info("closing ardoino_serial was unsucesful {}".format(e))

    def write_internal_actuator(self, write_value: int):
        self.ardoino_serial.remote_call(self.type_name, write_value)
        return 0
