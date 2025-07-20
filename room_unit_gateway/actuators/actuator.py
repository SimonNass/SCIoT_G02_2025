#!/usr/bin/env python
"""Module specifies the actuators."""

from typing import Union
try:
    import grovepi
    from grovepi import *
except ImportError:
    grovepi = None
import uuid
import time
from abc import ABC, abstractmethod
import logging
from enumdef import Connectortype
from iot_info import IoT_Info
logger = logging.getLogger(__name__)

class ActuatorInterface(ABC):
    def __init__(self, general_iot_device: IoT_Info, initial_value: Union[float, str], off_value: Union[float, str], impact_step_size: float):
        self.general_iot_device = general_iot_device
        self.initial_value = max(self.general_iot_device.min_value,min(self.general_iot_device.max_value,initial_value))
        self.last_value = self.initial_value
        self.last_value_timestamp = 0
        if not self.is_valid(self.initial_value):
            self.last_value = self.general_iot_device.min_value
        self.off_value = max(self.general_iot_device.min_value,min(self.general_iot_device.max_value,off_value))
        self.impact_step_size = impact_step_size
        self.value_has_changed = False

    @abstractmethod
    def __del__(self):
        pass

    def __str__(self):
        return str(self.__dict__())

    def __dict__(self):
        return_dict = {}
        return_dict.update(self.general_iot_device.__dict__())
        return_dict.update({"initial_value":self.initial_value, "off_value":self.off_value, "impact_step_size":self.impact_step_size, "is_off":self.is_off(), "last_value":self.last_value})
        return return_dict

    def write_actuator(self, value: float):
        time_now = time.time()
        if time_now - self.last_value_timestamp < 5:
            print("time to close")
            return
        write_value = max(self.general_iot_device.min_value,min(self.general_iot_device.max_value,value))
        if not self.is_valid(write_value):
            text = f"value {value} is out of the allowed interval [{self.general_iot_device.min_value},{self.general_iot_device.max_value}] for this actuator"
            raise ValueError(text)
        try:
            analog_set_value = self.write_internal_actuator(write_value)
            print(f'set to {analog_set_value}')
            self.last_value_timestamp = time.time()
            self.last_value = write_value
            self.general_iot_device.datatype = str(type(self.last_value))
            self.value_has_changed = True
            print (f"uuid: {self.general_iot_device.id}, device name: {self.general_iot_device.name}, value: {self.last_value}")
            logger.info(f"uuid: {self.general_iot_device.id}, device name: {self.general_iot_device.name}, value: {self.last_value}, type: {self.general_iot_device.datatype}")
        except (Exception, IOError, TypeError, AttributeError) as e:
            print ("write was unsucesful")
            #print (e)
            logger.error(f"{self.general_iot_device.name}: write was unsucesful {e}")

    @abstractmethod
    def write_internal_actuator(self, write_value: float):
        pass

    def is_valid(self, value: float):
        if (value > self.general_iot_device.max_value) or (value < self.general_iot_device.min_value):
            text = f"value {value} is out of the allowed interval [{self.general_iot_device.min_value},{self.general_iot_device.max_value}] for this actuator"
            print (f"uuid: {self.general_iot_device.id}, device name: {self.general_iot_device.name} {text}")
            logger.warning(f"uuid: {self.general_iot_device.id}, device name: {self.general_iot_device.name} {text}")
            return False
        return True

    def is_off(self):
        return self.last_value == self.off_value

class AnalogActuator(ActuatorInterface):
    def __init__(self, general_iot_device: IoT_Info, initial_value: float, off_value: float, impact_step_size: float):
        if general_iot_device.connector_type != Connectortype.Analog:
            raise ValueError("Connector_type is not Analog.")
        super().__init__(general_iot_device=general_iot_device,initial_value=initial_value,off_value=off_value, impact_step_size=impact_step_size)
        try:
            grovepi.pinMode(self.general_iot_device.i2c_connector,"OUTPUT")
        except  AttributeError as e:
            print ("pinMode was unsucesful")
            #print (e)
            logger.error(f"{self.general_iot_device.name}: pinMode was unsucesful {e}")
        self.write_actuator(self.initial_value)

    def __del__(self):
        try:
            grovepi.analogWrite(self.general_iot_device.i2c_connector,self.off_value)
        except (Exception, IOError, TypeError, AttributeError) as e:
            print ("write was unsucesful")
            #print (e)
            logger.error(f"{self.general_iot_device.name}: write was unsucesful {e}")

    def write_internal_actuator(self, write_value: float):
        print(f'{write_value} to {int(write_value)}')
        return grovepi.analogWrite(self.general_iot_device.i2c_connector,int(write_value))

class DigitalActuator(ActuatorInterface):
    def __init__(self, general_iot_device: IoT_Info, initial_value: float, off_value: float, impact_step_size: float):
        if general_iot_device.connector_type != Connectortype.Digital:
            raise ValueError("Connector_type is not Analog.")
        super().__init__(general_iot_device=general_iot_device,initial_value=initial_value,off_value=off_value, impact_step_size=impact_step_size)
        try:
            grovepi.pinMode(self.general_iot_device.i2c_connector,"OUTPUT")
        except  AttributeError as e:
            print ("pinMode was unsucesful")
            #print (e)
            logger.error(f"{self.general_iot_device.name}: pinMode was unsucesful {e}")
        self.write_actuator(self.initial_value)

    def __del__(self):
        try:
            grovepi.digitalWrite(self.general_iot_device.i2c_connector,self.off_value)
        except (Exception, IOError, TypeError, AttributeError) as e:
            print ("write was unsucesful")
            #print (e)
            logger.error(f"{self.general_iot_device.name}: write was unsucesful {e}")

    def write_internal_actuator(self, write_value: float):
        return grovepi.digitalWrite(self.general_iot_device.i2c_connector,int(write_value))

class VirtualActuator_numerical(ActuatorInterface):
    def __init__(self, general_iot_device: IoT_Info, initial_value: float, off_value: float, impact_step_size: float):
        if general_iot_device.connector_type != Connectortype.Virtual_numerical:
            raise ValueError("Connector_type is not Virtual.")
        super().__init__(general_iot_device=general_iot_device,initial_value=initial_value,off_value=off_value, impact_step_size=impact_step_size)
        self.write_actuator(self.initial_value)

    def __del__(self):
        pass

    def write_internal_actuator(self, write_value: float):
        return write_value
