"""Module specifies the actuators on the arduino."""

import logging
from actuators.actuator import ActuatorInterface
from enumdef import Connectortype
from networking.ardoino_reverse_proxy import ArdoinoReverseProxy
from iot_info import IoT_Info
logger = logging.getLogger(__name__)

class ArdoinoActuator(ActuatorInterface):
    def __init__(self, general_iot_device: IoT_Info, initial_value: float, off_value: float, impact_step_size: float, ardoino_serial: ArdoinoReverseProxy, type_name_ardoino: str):
        #if connector_types != Connectortype.Analog:
        #    raise ValueError("Connector_type is not Analog.")
        super().__init__(general_iot_device=general_iot_device,initial_value=initial_value,off_value=off_value, impact_step_size=impact_step_size)
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

    def write_internal_actuator(self, write_value: float):
        #self.ardoino_serial.remote_call(self.type_name_ardoino, write_value)
        return 0
