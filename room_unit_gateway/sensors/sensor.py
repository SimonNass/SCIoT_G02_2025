#!/usr/bin/env python

import grovepi
from grovepi import *
import numpy as np
import uuid
from abc import ABC, abstractmethod

from enumdef import Connectortype, Notifyinterval

class SensorInterface(ABC):
    def __init__(self, name: str, type_name: str, connector: int, connector_types: Connectortype, min_value: int, max_value: int, datatype: str, unit: str, read_interval: int, notify_interval: Notifyinterval, notify_change_precision: int):
        self.id = uuid.uuid1()
        self.name = name
        self.type = type_name
        self.i2c_connector = connector #assert not used twice
        self.connector_type = connector_types
        self.min_value = min_value
        self.max_value = max_value
        self.datatype = datatype
        self.unit = unit
        self.read_interval = read_interval
        self.notify_interval = notify_interval
        self.notify_change_precision = notify_change_precision
        self.last_value = self.min_value

    def __str__(self):
        return "ID:{},Name:{},Type:{},I2C:{},{},last value:{},read interval:{}".format(self.id,self.name,self.type,self.i2c_connector,self.connector_type,self.last_value,self.read_interval)

    def __dict__(self):
        return {"id":self.id,"name":self.name,"type":self.type,"i2c":self.i2c_connector,"connector_type":self.connector_type,"last_value":self.last_value, "read_interval":self.read_interval}

    @abstractmethod
    def read_sensor(self):
        pass

class AnalogSensor(SensorInterface):
    def __init__(self, name: str, type_name: str, connector: int, connector_types: Connectortype, min_value: int, max_value: int, datatype: str, unit: str, read_interval: int, notify_interval: Notifyinterval, notify_change_precision: int):
        if connector_types != Connectortype.Analog:
            raise ValueError("Connector_type is not Analog.")
        super.__init__(name=name, type_name=type_name, connector=connector, connector_types=connector_types, min_value=min_value, max_value=max_value, datatype=datatype, unit=unit, read_interval=read_interval, notify_interval=notify_interval, notify_change_precision=notify_change_precision)
        self.last_value = self.read_sensor()

    def read_sensor(self):
        try:
            self.last_value = grovepi.analogRead(self.i2c_connector)
            print ("{}: {}".format(self.name,self.last_value))
            return self.last_value
        except Exception as e:
            print ("read was unsucesful")
            print (e)

class DigitalSensor(SensorInterface):
    def __init__(self, name: str, type_name: str, connector: int, connector_types: Connectortype, min_value: int, max_value: int, datatype: str, unit: str, read_interval: int, notify_interval: Notifyinterval, notify_change_precision: int):
        if self.connector_type != Connectortype.Digital:
            raise ValueError("connector_type is not Digital.")
        super.__init__(name=name, type_name=type_name, connector=connector, connector_types=connector_types, min_value=min_value, max_value=max_value, datatype=datatype, unit=unit, read_interval=read_interval, notify_interval=notify_interval, notify_change_precision=notify_change_precision)
        grovepi.pinMode(self.i2c_connector,"INPUT")
        self.last_value = self.read_sensor()

    def __str__(self):
        return "ID:{},Name:{},Type:{},I2C:{},{},last value:{},read interval:{}".format(self.id,self.name,self.type,self.i2c_connector,self.connector_type,self.last_value,self.read_interval)

    def __dict__(self):
        return {"id":self.id,"name":self.name,"type":self.type,"i2c":self.i2c_connector,"connector_type":self.connector_type,"last_value":self.last_value, "read_interval":self.read_interval}

    def read_sensor(self):
        try:
            self.last_value = grovepi.digitalRead(self.i2c_connector)
            print ("{}: {}".format(self.name,self.last_value))
            return self.last_value
        except Exception as e:
            print ("read was unsucesful")
            print (e)

class DigitalMultipleSensor(SensorInterface):
    def __init__(self, name: str, type_name: str, connector: int, connector_types: Connectortype, i: int, min_value: int, max_value: int, datatype: str, unit: str, read_interval: int, notify_interval: Notifyinterval, notify_change_precision: int):
        if (self.connector_type != Connectortype.Digital_multiple_0) or (self.connector_type != Connectortype.Digital_multiple_1):
            raise ValueError("connector_type is not Digital_multiple.")
        super.__init__(name=name, type_name=type_name, connector=connector, connector_types=connector_types, min_value=min_value, max_value=max_value, datatype=datatype, unit=unit, read_interval=read_interval, notify_interval=notify_interval, notify_change_precision=notify_change_precision)
        self.i = i
        grovepi.pinMode(self.i2c_connector,"INPUT")
        self.last_value = self.read_sensor()

    def __str__(self):
        return "ID:{},Name:{},Type:{},I2C:{},{},last value:{},read interval:{}".format(self.id,self.name,self.type,self.i2c_connector,self.connector_type,self.last_value,self.read_interval)

    def __dict__(self):
        return {"id":self.id,"name":self.name,"type":self.type,"i2c":self.i2c_connector,"connector_type":self.connector_type,"last_value":self.last_value, "read_interval":self.read_interval}

    def read_sensor(self):
        try:
            while True:
                    self.last_value = grovepi.dht(self.i2c_connector,0)[self.i]
                    if not any(np.isnan([self.last_value])):
                        break
            print ("{}: {}".format(self.name,self.last_value))
            return self.last_value
        except Exception as e:
            print ("read was unsucesful")
            print (e)
