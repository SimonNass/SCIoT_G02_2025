"""Module specifies the actuators on the arduino."""

import logging
from actuators.actuator import ActuatorInterface
from enumdef import Connectortype
from networking.ardoino_reverse_proxy import ArdoinoReverseProxy
logger = logging.getLogger(__name__)

class ArdoinoActuator(ActuatorInterface):
    def __init__(self, name: str, type_name: str, connector: int, connector_types: Connectortype, min_value: int, max_value: int, datatype: str, unit: str, initial_value: int, off_value: int, ardoino_serial: ArdoinoReverseProxy, type_name_ardoino: str):
        #if connector_types != Connectortype.Analog:
        #    raise ValueError("Connector_type is not Analog.")
        super().__init__(name=name,type_name=type_name,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value,datatype=datatype,unit=unit,initial_value=initial_value,off_value=off_value)
        self.type_name_ardoino = type_name_ardoino
        # in bps
        self.ardoino_serial = ardoino_serial
        self.write_actuator(self.initial_value)

    def __del__(self):
        try:
            del self.ardoino_serial
        except (Exception, IOError, TypeError, AttributeError) as e:
            print ("closing ardoino_serial was unsucesful")
            #print (e)
            logger.error(f"closing ardoino_serial was unsucesful {e}")

    def write_internal_actuator(self, write_value: int):
        self.ardoino_serial.remote_call(self.type_name_ardoino, write_value)
        return 0
