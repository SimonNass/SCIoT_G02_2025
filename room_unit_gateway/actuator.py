#!/usr/bin/env python

import grovepi
from grovepi import *

from enumdef import Connectortype

class Actuator:
    def __init__(self, id: int, name: str, actuator_type: str, i2c: int, i2c_type: Connectortype, initial_value: int, min_value: int, max_value: int):
        self.id = id #assert unique
        self.name = name
        self.type = actuator_type
        self.i2c_connector = i2c #assert not used twice
        self.connector_type = i2c_type
        self.last_value = max(min_value,min(max_value,initial_value))
        self.min_value = min_value
        self.max_value = max_value
        if min_value > max_value:
            self.min_value = max_value
            self.max_value = min_value
        if not self.is_valid(initial_value):
            self.last_value = min_value
        grovepi.pinMode(self.i2c_connector,"OUTPUT")
        self.write_actuator(self.last_value)

    def __del__(self):
        if Connectortype.Analog:
            grovepi.analogWrite(self.i2c_connector,0)
        elif Connectortype.Digital:
            grovepi.digitalWrite(self.i2c_connector,0)

    def __str__(self):
        return "ID:{},Name:{},Type:{},I2C:{},{},last value:{},min:{},max:{}".format(self.id,self.name,self.type,self.i2c_connector,self.connector_type,self.last_value,self.min_value,self.max_value)

    def write_actuator(self, value: int):
        write_value = max(self.min_value,min(self.max_value,value))
        try:
            if not self.is_valid(write_value):
                text = "value {} is out of the allowed interval [{},{}] for this actuator".format(value,self.min_value,self.max_value)
                raise ValueError(text)

            if self.connector_type == Connectortype.Analog:
                self.last_value = grovepi.analogWrite(self.i2c_connector,write_value)
            elif self.connector_type == Connectortype.Digital:
                self.last_value = grovepi.digitalWrite(self.i2c_connector,write_value)
            elif self.connector_type == Connectortype.Digital_multiple:
                raise ValueError("Connector type is not implemented")
            elif self.connector_type == Connectortype.I2C:
                raise ValueError("Connector type is not implemented")
            else:
                raise ValueError("Connector type is uncnown")
            self.last_value = write_value
            print ("{}: {}".format(self.name,self.last_value))
        except Exception as e:
            print ("write was unsucesful")
            print (e)

    def is_valid(self, value: int):
        if (value > self.max_value) or (value < self.min_value):
            text = "value {} is out of the allowed interval [{},{}] for this actuator".format(value,self.min_value,self.max_value)
            print (text)
            return False
        return True
