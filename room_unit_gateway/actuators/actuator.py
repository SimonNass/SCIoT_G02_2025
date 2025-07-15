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
logger = logging.getLogger(__name__)

class ActuatorInterface(ABC):
    def __init__(self, name: str, type_name: str, connector: int, room_position: str, ai_planing_type: str, connector_types: Connectortype, min_value: Union[int, str], max_value: Union[int, str], datatype: str, unit: str, initial_value: Union[int, str], off_value: Union[int, str]):
        self.id = uuid.uuid1()
        self.name = name
        self.type = type_name
        self.room_position = room_position
        self.ai_planing_type = ai_planing_type
        self.i2c_connector = connector #assert not used twice
        self.connector_type = connector_types
        self.min_value = min_value
        self.max_value = max_value
        if min_value > max_value:
            self.min_value = max_value
            self.max_value = min_value
        self.datatype = datatype
        self.unit = unit
        self.initial_value = max(min_value,min(max_value,initial_value))
        self.last_value = self.initial_value
        self.last_value_timestamp = time.time()
        if not self.is_valid(self.initial_value):
            self.last_value = min_value
        self.off_value = max(min_value,min(max_value,off_value))
        self.value_has_changed = False

    @abstractmethod
    def __del__(self):
        pass

    def __str__(self):
        return str(self.__dict__())

    def __dict__(self):
        return {"id":str(self.id),"name":self.name,"type_name":self.type,"room_position":self.room_position,"ai_planing_type":self.ai_planing_type,"connector":self.i2c_connector,"connector_type":str(self.connector_type),"min":self.min_value, "max":self.max_value, "datatype":self.datatype, "unit":self.unit, "initial_value":self.initial_value, "off_value":self.off_value, "is_off":self.is_off(), "last_value":self.last_value}

    def write_actuator(self, value: int):
        write_value = max(self.min_value,min(self.max_value,value))
        if not self.is_valid(write_value):
            text = f"value {value} is out of the allowed interval [{self.min_value},{self.max_value}] for this actuator"
            raise ValueError(text)
        try:
            _ = self.write_internal_actuator(write_value)
            self.last_value_timestamp = time.time()
            self.last_value = write_value
            self.datatype = str(type(self.last_value))
            self.value_has_changed = True
            print (f"uuid: {self.id}, device name: {self.name}, value: {self.last_value}")
            logger.info(f"uuid: {self.id}, device name: {self.name}, value: {self.last_value}, type: {self.datatype}")
        except (Exception, IOError, TypeError, AttributeError) as e:
            print ("write was unsucesful")
            #print (e)
            logger.error(f"{self.name}: write was unsucesful {e}")

    @abstractmethod
    def write_internal_actuator(self, write_value: int):
        pass

    def is_valid(self, value: int):
        if (value > self.max_value) or (value < self.min_value):
            text = f"value {value} is out of the allowed interval [{self.min_value},{self.max_value}] for this actuator"
            print (text)
            return False
        return True

    def is_off(self):
        return self.last_value == self.off_value

class AnalogActuator(ActuatorInterface):
    def __init__(self, name: str, type_name: str, room_position: str, ai_planing_type: str, connector: int, connector_types: Connectortype, min_value: int, max_value: int, datatype: str, unit: str, initial_value: int, off_value: int):
        if connector_types != Connectortype.Analog:
            raise ValueError("Connector_type is not Analog.")
        super().__init__(name=name,type_name=type_name, room_position=room_position, ai_planing_type=ai_planing_type,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value,datatype=datatype,unit=unit,initial_value=initial_value,off_value=off_value)
        try:
            grovepi.pinMode(self.i2c_connector,"OUTPUT")
        except  AttributeError as e:
            print ("pinMode was unsucesful")
            #print (e)
            logger.error(f"{self.name}: pinMode was unsucesful {e}")
        self.write_actuator(self.initial_value)

    def __del__(self):
        try:
            grovepi.analogWrite(self.i2c_connector,self.off_value)
        except (Exception, IOError, TypeError, AttributeError) as e:
            print ("write was unsucesful")
            #print (e)
            logger.error(f"{self.name}: write was unsucesful {e}")

    def write_internal_actuator(self, write_value: int):
        return grovepi.analogWrite(self.i2c_connector,write_value)

class DigitalActuator(ActuatorInterface):
    def __init__(self, name: str, type_name: str, room_position: str, ai_planing_type: str, connector: int, connector_types: Connectortype, min_value: int, max_value: int, datatype: str, unit: str, initial_value: int, off_value: int):
        if connector_types != Connectortype.Digital:
            raise ValueError("Connector_type is not Analog.")
        super().__init__(name=name,type_name=type_name, room_position=room_position, ai_planing_type=ai_planing_type,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value,datatype=datatype,unit=unit,initial_value=initial_value,off_value=off_value)
        try:
            grovepi.pinMode(self.i2c_connector,"OUTPUT")
        except  AttributeError as e:
            print ("pinMode was unsucesful")
            #print (e)
            logger.error(f"{self.name}: pinMode was unsucesful {e}")
        self.write_actuator(self.initial_value)

    def __del__(self):
        try:
            grovepi.digitalWrite(self.i2c_connector,self.off_value)
        except (Exception, IOError, TypeError, AttributeError) as e:
            print ("write was unsucesful")
            #print (e)
            logger.error(f"{self.name}: write was unsucesful {e}")

    def write_internal_actuator(self, write_value: int):
        return grovepi.digitalWrite(self.i2c_connector,write_value)

class VirtualActuator_numerical(ActuatorInterface):
    def __init__(self, name: str, type_name: str, connector: int, room_position: str, ai_planing_type: str, connector_types: Connectortype, min_value: int, max_value: int, datatype: str, unit: str, initial_value: int, off_value: int):
        if connector_types != Connectortype.Virtual_numerical:
            raise ValueError("Connector_type is not Virtual.")
        super().__init__(name=name,type_name=type_name, room_position=room_position, ai_planing_type=ai_planing_type,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value,datatype=datatype,unit=unit,initial_value=initial_value,off_value=off_value)
        self.write_actuator(self.initial_value)

    def __del__(self):
        pass

    def write_internal_actuator(self, write_value: int):
        return write_value
