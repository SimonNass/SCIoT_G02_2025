#!/usr/bin/env python

import grovepi
from grovepi import *

from enumdef import Connectortype

class Actuator:
    def __init__(self, id, name, actuator_type, i2c, i2c_type, initial_value, min, max):
        self.id = id #assert unique
        self.name = name
        self.type = actuator_type
        self.i2c_connector = i2c #assert not used twice
        self.connector_type = i2c_type
        self.last_value = initial_value
        if initial_value > max or initial_value < min:
            self.last_value = min
            text = "value {} is out of the allowed interval [{},{}]for this actuator".format(initial_value,min,max)
	    raise ValueError(text)
        self.min_value = int(min)
        self.max_value = int(max)
        if min > max:
            self.min_value = max
            self.max_value = min
            raise ValueError("The min and max values are swapped")
        grovepi.pinMode(self.i2c_connector,"OUTPUT")
        self.write_actuator(initial_value)

    def __del__(self):
        if Connectortype.Analog:
            grovepi.analogWrite(self.i2c_connector,0)
        elif Connectortype.Digital:
            grovepi.digitalWrite(self.i2c_connector,0)

    def __str__(self):
        return "ID:{},Name:{},Type:{},I2C:{},{},last value:{},min:{},max:{}".format(self.id,self.name,self.type,self.i2c_connector,self.connector_type,self.last_value,self.min_value,self.max_value)

    def write_actuator(self, value):
        if (int(value) > self.max_value) or (int(value) < self.min_value):
            text = "value {} is out of the allowed interval [{},{}] for this actuator".format(value,self.min_value,self.max_value)
	    print ("{} < {} == {}".format(int(value)+10,self.min_value, int(value)+10 < self.min_value))
	    raise ValueError(text)

        if self.connector_type == Connectortype.Analog:
            self.last_value = grovepi.analogWrite(self.i2c_connector,int(value))
        elif self.connector_type == Connectortype.Digital:
            self.last_value = grovepi.digitalWrite(self.i2c_connector,int(value))
        elif self.connector_type == Connectortype.Digital_multiple:
            raise ValueError("Connector type is not implemented")
        elif self.connector_type == Connectortype.I2C:
            raise ValueError("Connector type is not implemented")
        else:
            raise ValueError("Connector type is uncnown")
        self.last_value = value
        print ("{}: {}".format(self.name,self.last_value))
