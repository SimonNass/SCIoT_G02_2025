#!/usr/bin/env python

from typing import Union
import grovepi
from grovepi import *
import uuid
from abc import ABC, abstractmethod

from enumdef import Connectortype

class ActuatorInterface(ABC):
    def __init__(self, name: str, type_name: str, connector: int, connector_types: Connectortype, min_value: Union[int, str], max_value: Union[int, str], datatype: str, unit: str, initial_value: Union[int, str], off_value: Union[int, str]):
        self.id = uuid.uuid1()
        self.name = name
        self.type = type_name
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
        if not self.is_valid(self.initial_value):
            self.last_value = min_value
        self.off_value = max(min_value,min(max_value,off_value))
        grovepi.pinMode(self.i2c_connector,"OUTPUT")

    @abstractmethod
    def __del__(self):
        pass

    def __str__(self):
        return str(self.__dict__())

    def __dict__(self):
        return {"id":str(self.id),"name":self.name,"type_name":self.type,"connector":self.i2c_connector,"connector_type":str(self.connector_type),"min":self.min_value, "max":self.max_value, "datatype":self.datatype, "unit":self.unit, "initial_value":self.initial_value, "off_value":self.off_value, "last_value":self.last_value}

    def write_actuator(self, value: int):
        write_value = max(self.min_value,min(self.max_value,value))
        if not self.is_valid(write_value):
            text = "value {} is out of the allowed interval [{},{}] for this actuator".format(value,self.min_value,self.max_value)
            raise ValueError(text)
        try:
            _ = self.write_internal_actuator(write_value)
            self.last_value = write_value
            print ("{}: {}".format(self.name,self.last_value))
        except Exception as e:
            print ("write was unsucesful")
            print (e)

    @abstractmethod
    def write_internal_actuator(self, value: int):
        pass

    def is_valid(self, value: int):
        if (value > self.max_value) or (value < self.min_value):
            text = "value {} is out of the allowed interval [{},{}] for this actuator".format(value,self.min_value,self.max_value)
            print (text)
            return False
        return True

class AnalogActuator(ActuatorInterface):
    def __init__(self, name: str, type_name: str, connector: int, connector_types: Connectortype, min_value: int, max_value: int, datatype: str, unit: str, initial_value: int, off_value: int):
        if connector_types != Connectortype.Analog:
            raise ValueError("Connector_type is not Analog.")
        super().__init__(name=name,type_name=type_name,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value,datatype=datatype,unit=unit,initial_value=initial_value,off_value=off_value)
        self.write_actuator(self.initial_value)

    def __del__(self):
        grovepi.analogWrite(self.i2c_connector,self.off_value)

    def write_internal_actuator(self, write_value: int):
        return grovepi.analogWrite(self.i2c_connector,write_value)

class DigitalActuator(ActuatorInterface):
    def __init__(self, name: str, type_name: str, connector: int, connector_types: Connectortype, min_value: int, max_value: int, datatype: str, unit: str, initial_value: int, off_value: int):
        if connector_types != Connectortype.Digital:
            raise ValueError("Connector_type is not Analog.")
        super().__init__(name=name,type_name=type_name,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value,datatype=datatype,unit=unit,initial_value=initial_value,off_value=off_value)
        self.write_actuator(self.initial_value)

    def __del__(self):
        grovepi.digitalWrite(self.i2c_connector,self.off_value)

    def write_internal_actuator(self, write_value: int):
        return grovepi.digitalWrite(self.i2c_connector,write_value)
