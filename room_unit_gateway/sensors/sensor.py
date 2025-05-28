#!/usr/bin/env python

import grovepi
from grovepi import *
import numpy as np
import uuid

from enumdef import Connectortype

class Sensor:
    def __init__(self, name: str, type_name: str, connector: int, connector_types: Connectortype, min_value: int, max_value: int, datatype: str, unit: str, read_interval: int):
        self.id = uuid.uuid1()
        self.name = name
        self.type = type_name
        self.i2c_connector = connector #assert not used twice
        self.connector_type = connector_types
        self.read_interval = read_interval
        #print ("{}".format(self.connector_type))
        if self.connector_type == Connectortype.Digital:
            grovepi.pinMode(self.i2c_connector,"INPUT")
        self.last_value = self.read_sensor()

    def __str__(self):
        return "ID:{},Name:{},Type:{},I2C:{},{},last value:{},read interval:{}".format(self.id,self.name,self.type,self.i2c_connector,self.connector_type,self.last_value,self.read_interval)

    def __dict__(self):
        return {"id":self.id,"name":self.name,"type":self.type,"i2c":self.i2c_connector,"connector_type":self.connector_type,"last_value":self.last_value, "read_interval":self.read_interval}

    def read_sensor(self):
        try:
            if self.connector_type == Connectortype.Analog:
                self.last_value = grovepi.analogRead(self.i2c_connector)
            elif self.connector_type == Connectortype.Digital:
                self.last_value = grovepi.digitalRead(self.i2c_connector)
            elif self.connector_type == Connectortype.Digital_multiple:
                while True:
                    self.last_value = grovepi.dht(self.i2c_connector,0)
                    if not any(np.isnan(self.last_value)):
                        break
            elif self.connector_type == Connectortype.I2C:
                raise ValueError("Connector type is not implemented")
            else:
                raise ValueError("Connector type is uncnown")

            print ("{}: {}".format(self.name,self.last_value))
            return self.last_value
        except Exception as e:
            print ("read was unsucesful")
            print (e)
