#!/usr/bin/env python
"""Module specifies the text based actuators."""

try:
    import grovepi
    from grove_rgb_lcd import *
except ImportError:
    grovepi = None
    grove_rgb_lcd = None
import time
import logging
from enumdef import Connectortype
from actuators.actuator import ActuatorInterface
from iot_info import IoT_Info
logger = logging.getLogger(__name__)

class AbstractActuator_textual(ActuatorInterface):
    def __init__(self, general_iot_device: IoT_Info, initial_value: str, off_value: str, impact_step_size: float, char_limit_per_line: int, char_limit_lines: int):
        self.char_limit = char_limit_per_line * char_limit_lines
        general_iot_device.min_value = 0
        general_iot_device.max_value = self.char_limit
        super().__init__(general_iot_device=general_iot_device,initial_value=0,off_value=0, impact_step_size=impact_step_size)
        self.initial_value = initial_value
        self.last_value = self.initial_value
        self.last_value_timestamp = time.time()
        self.off_value = off_value

    def write_actuator(self, value: str):
        write_value = value
        try:
            if len(write_value) > self.char_limit:
                print ("Text is too long")
                logger.warning(f"{self.general_iot_device.name}: {write_value} Text is too long")
                write_value = write_value[:self.char_limit]
            _ = self.write_internal_actuator(write_value)
            self.last_value_timestamp = time.time()
            self.last_value = write_value
            self.datatype = str(type(self.last_value))
            self.value_has_changed = True
            print (f"uuid: {self.general_iot_device.id}, device name: {self.general_iot_device.name}, value: {self.last_value}")
            logger.info(f"uuid: {self.general_iot_device.id}, device name: {self.general_iot_device.name}, value: {self.last_value}, type: {self.datatype}")
        except Exception as e:
            print ("write was unsucesful")
            logger.error(f"{self.general_iot_device.name}: write was unsucesful {e}")

    def is_valid(self, value: str):
        if len(str(value)) > self.char_limit:
            text = f"value {value} is out of the allowed interval / Text is too long {len(value)} > {self.char_limit} for this actuator"
            print (text)
            return False
        return True

class DisplayActuator(AbstractActuator_textual):
    def __init__(self, general_iot_device: IoT_Info, initial_value: str, off_value: str, impact_step_size: float):
        if general_iot_device.connector_type != Connectortype.I2C_display:
            raise ValueError("Connector_type is not a display.")
        super().__init__(general_iot_device=general_iot_device,initial_value=initial_value,off_value=off_value, impact_step_size=impact_step_size, char_limit_per_line=16, char_limit_lines=2)
        r, g, b, text = self.split_state_info(self.initial_value)
        try:
            setRGB(r,g,b)
        except  (Exception, AttributeError) as e:
            print ("setRGB was unsucesful")
            #print (e)
            logger.error(f"{self.general_iot_device.name}: setRGB was unsucesful {e}")
        self.write_actuator(text)

    def __del__(self):
        r, g, b, text = self.split_state_info(self.off_value)
        try:
            setText(text)
            setRGB(r,g,b)
        except  (Exception, AttributeError) as e:
            print ("setRGB or setText was unsucesful")
            #print (e)
            logger.error(f"{self.general_iot_device.name}: setRGB or setText was unsucesful {e}")

    def write_internal_actuator(self, write_value: str):
        setText(write_value)
        return write_value

    def split_state_info(self, write_value: str):
        split = write_value.split(",")
        r = int(split[0])
        g = int(split[1])
        b = int(split[2])
        text = split[3]
        return r, g, b, text

class VirtualActuator_textual(AbstractActuator_textual):
    def __init__(self, general_iot_device: IoT_Info, initial_value: str, off_value: str, impact_step_size: float):
        if general_iot_device.connector_type != Connectortype.Virtual_textual:
            raise ValueError("Connector_type is not Virtual_textual.")
        super().__init__(general_iot_device=general_iot_device,initial_value=initial_value, off_value=off_value, impact_step_size=impact_step_size, char_limit_per_line=16, char_limit_lines=2)
        self.write_actuator(self.initial_value)

    def __del__(self):
        pass

    def write_internal_actuator(self, write_value: str):
        return write_value
