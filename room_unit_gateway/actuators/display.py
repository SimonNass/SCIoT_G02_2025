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
logger = logging.getLogger(__name__)

class AbstractActuator_textual(ActuatorInterface):
    def __init__(self, name: str, type_name: str, room_position: str, ai_planing_type: str, connector: int, connector_types: Connectortype, min_value: int, max_value: int, datatype: str, unit: str, initial_value: str, off_value: str, char_limit_per_line: int, char_limit_lines: int):
        self.char_limit = char_limit_per_line * char_limit_lines
        super().__init__(name=name,type_name=type_name, room_position=room_position, ai_planing_type=ai_planing_type,connector=connector,connector_types=connector_types,min_value=0,max_value=self.char_limit,datatype=datatype,unit=unit,initial_value=0,off_value=0)
        self.initial_value = initial_value
        self.last_value = self.initial_value
        self.last_value_timestamp = time.time()
        self.off_value = off_value

    def write_actuator(self, value: str):
        write_value = value
        try:
            if len(write_value) > self.char_limit:
                print ("Text is too long")
                logger.warning(f"{self.name}: {write_value} Text is too long")
                write_value = write_value[:self.char_limit]
            _ = self.write_internal_actuator(write_value)
            self.last_value_timestamp = time.time()
            self.last_value = write_value
            self.datatype = str(type(self.last_value))
            self.value_has_changed = True
            print (f"uuid: {self.id}, device name: {self.name}, value: {self.last_value}")
            logger.info(f"uuid: {self.id}, device name: {self.name}, value: {self.last_value}, type: {self.datatype}")
        except Exception as e:
            print ("write was unsucesful")
            logger.error(f"{self.name}: write was unsucesful {e}")

    def is_valid(self, value: str):
        if len(str(value)) > self.char_limit:
            text = f"value {value} is out of the allowed interval / Text is too long {len(value)} > {self.char_limit} for this actuator"
            print (text)
            return False
        return True

class DisplayActuator(AbstractActuator_textual):
    def __init__(self, name: str, type_name: str, room_position: str, ai_planing_type: str, connector: int, connector_types: Connectortype, min_value: int, max_value: int, datatype: str, unit: str, initial_value: str, off_value: str):
        if connector_types != Connectortype.I2C_display:
            raise ValueError("Connector_type is not a display.")
        super().__init__(name=name,type_name=type_name, room_position=room_position, ai_planing_type=ai_planing_type,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value,datatype=datatype,unit=unit,initial_value=initial_value,off_value=off_value, char_limit_per_line=16, char_limit_lines=2)
        r, g, b, text = self.split_state_info(self.initial_value)
        try:
            setRGB(r,g,b)
        except  (Exception, AttributeError) as e:
            print ("setRGB was unsucesful")
            #print (e)
            logger.error(f"{self.name}: setRGB was unsucesful {e}")
        self.write_actuator(text)

    def __del__(self):
        r, g, b, text = self.split_state_info(self.off_value)
        try:
            setText(text)
            setRGB(r,g,b)
        except  (Exception, AttributeError) as e:
            print ("setRGB or setText was unsucesful")
            #print (e)
            logger.error(f"{self.name}: setRGB or setText was unsucesful {e}")

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
    def __init__(self, name: str, type_name: str, room_position: str, ai_planing_type: str, connector: int, connector_types: Connectortype, min_value: int, max_value: int, datatype: str, unit: str, initial_value: str, off_value: str):
        if connector_types != Connectortype.Virtual_textual:
            raise ValueError("Connector_type is not Virtual_textual.")
        super().__init__(name=name,type_name=type_name, room_position=room_position, ai_planing_type=ai_planing_type,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value,datatype=datatype,unit=unit,initial_value=initial_value,off_value=off_value, char_limit_per_line=16, char_limit_lines=2)
        self.write_actuator(self.initial_value)

    def __del__(self):
        pass

    def write_internal_actuator(self, write_value: int):
        return write_value
