#!/usr/bin/env python

import grovepi

from enumdef import Connectortype

class Actuator:
    def __init__(self, id: int, name: str, actuator_type: str, i2c: int, i2c_type: Connectortype, initial_value: int, min: int, max: int):
        self.id = id #assert unique
        self.name = name
        self.type = actuator_type
        self.i2c_connector = i2c #assert not used twice
        self.connector_type = i2c_type
        self.last_value = initial_value
        if initial_value > self.max_value or initial_value < self.min_value:
            self.last_value = min
            raise ValueError("value is out of the allowed interval for this actuator")
        self.min_value = min
        self.max_value = max
        if min > max:
            self.min_value = max
            self.max_value = min
            raise ValueError("The min and max values are swapped")
        if Connectortype.Digital:
            grovepi.pinMode(self.i2c_connector,"OUTPUT")
        self.write_actuator(initial_value)

    def __del__(self):
        if Connectortype.Analog:
            grovepi.analogWrite(self.i2c_connector,0)
        elif Connectortype.Digital:
            grovepi.digitalWrite(self.i2c_connector,0)

    def __str__(self):
        return f"ID:{self.id},Name:{self.name},Type:{self.type},I2C:{self.i2c_connector},{self.connector_type},last value:{self.last_value},min:{self.min_value},max:{self.max_value}"
    
    def write_actuator(self, value: int):
        if value > self.max_value or value < self.min_value:
            raise ValueError("value is out of the allowed interval for this actuator")

        if self.connector_type == Connectortype.Analog:
            self.last_value = grovepi.analogWrite(self.i2c_connector,value)
        elif self.connector_type == Connectortype.Digital:
            self.last_value = grovepi.digitalWrite(self.i2c_connector,value)
        elif self.connector_type == Connectortype.Digital_multiple:
            raise ValueError("Connector type is not implemented")
        elif self.connector_type == Connectortype.I2C:
            raise ValueError("Connector type is not implemented")
        else:
            raise ValueError("Connector type is uncnown")
        self.last_value = value
        print ("{}: {}".format(self.name,self.last_value))
