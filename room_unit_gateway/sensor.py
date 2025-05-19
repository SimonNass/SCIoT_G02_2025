#!/usr/bin/env python

import grovepi
from grovepi import *

from enumdef import Connectortype

class Sensor:
    def __init__(self, id, name, sensore_type, i2c, i2c_type, read_interval):
        self.id = id #assert unique
        self.name = name
        self.type = sensore_type
        self.i2c_connector = i2c #assert not used twice
        self.connector_type = i2c_type
        self.read_interval = read_interval
        if Connectortype.Digital:
            grovepi.pinMode(self.i2c_connector,"INPUT")
        self.last_value = self.read_sensor()

    #def __del__(self):
    #    pass

    def __str__(self):
        return "ID:{},Name:{},Type:{},I2C:{},{},last value:{}".format(self.id,self.name,self.type,self.i2c_connector,self.connector_type,self.last_value)

    def read_sensor(self):
        if self.connector_type == Connectortype.Analog:
            self.last_value = grovepi.analogRead(self.i2c_connector)
        elif self.connector_type == Connectortype.Digital:
            self.last_value = grovepi.digitalRead(self.i2c_connector)
        elif self.connector_type == Connectortype.Digital_multiple:
            self.last_value = grovepi.dht(self.i2c_connector,0)
        elif self.connector_type == Connectortype.I2C:
            raise ValueError("Connector type is not implemented")
        else:
            raise ValueError("Connector type is uncnown")
        print ("{}: {}".format(self.name,self.last_value))
        return self.last_value
