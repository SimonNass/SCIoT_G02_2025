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
        return str(self.__dict__())

    def __dict__(self):
        return {"id":str(self.id),"name":self.name,"type_name":self.type,"connector":self.i2c_connector,"connector_type":str(self.connector_type),"min":self.min_value, "max":self.max_value, "datatype":self.datatype, "unit":self.unit, "read_interval":self.read_interval, "notify_interval":str(self.notify_interval), "notify_change_precision":self.notify_change_precision, "last_value":self.last_value}

    def read_sensor(self):
        try:
            self.last_value = self.read_internal_sensor()
            print ("{}: {}".format(self.name,self.last_value))
            return self.__dict__()
        except (Exception, IOError, TypeError) as e:
            print ("read was unsucesful")
            print (e)

    @abstractmethod
    def read_internal_sensor(self):
        pass

class AnalogSensor(SensorInterface):
    def __init__(self, name: str, type_name: str, connector: int, connector_types: Connectortype, min_value: int, max_value: int, datatype: str, unit: str, read_interval: int, notify_interval: Notifyinterval, notify_change_precision: int):
        if connector_types != Connectortype.Analog:
            raise ValueError("Connector_type is not Analog.")
        super().__init__(name=name, type_name=type_name, connector=connector, connector_types=connector_types, min_value=min_value, max_value=max_value, datatype=datatype, unit=unit, read_interval=read_interval, notify_interval=notify_interval, notify_change_precision=notify_change_precision)
        _ = self.read_sensor()

    def read_internal_sensor(self):
        return grovepi.analogRead(self.i2c_connector)

class DigitalSensor(SensorInterface):
    def __init__(self, name: str, type_name: str, connector: int, connector_types: Connectortype, min_value: int, max_value: int, datatype: str, unit: str, read_interval: int, notify_interval: Notifyinterval, notify_change_precision: int):
        if connector_types != Connectortype.Digital:
            raise ValueError("connector_type is not Digital.")
        super().__init__(name=name, type_name=type_name, connector=connector, connector_types=connector_types, min_value=min_value, max_value=max_value, datatype=datatype, unit=unit, read_interval=read_interval, notify_interval=notify_interval, notify_change_precision=notify_change_precision)
        grovepi.pinMode(self.i2c_connector,"INPUT")
        _ = self.read_sensor()

    def read_internal_sensor(self):
        return grovepi.digitalRead(self.i2c_connector)

class DigitalMultipleSensor(SensorInterface):
    def __init__(self, name: str, type_name: str, connector: int, connector_types: Connectortype, i: int, min_value: int, max_value: int, datatype: str, unit: str, read_interval: int, notify_interval: Notifyinterval, notify_change_precision: int):
        if not ((connector_types == Connectortype.Digital_multiple_0) or (connector_types == Connectortype.Digital_multiple_1)):
            raise ValueError("connector_type is not Digital_multiple.")
        super().__init__(name=name, type_name=type_name, connector=connector, connector_types=connector_types, min_value=min_value, max_value=max_value, datatype=datatype, unit=unit, read_interval=read_interval, notify_interval=notify_interval, notify_change_precision=notify_change_precision)
        self.i = i
        grovepi.pinMode(self.i2c_connector,"INPUT")
        _ = self.read_sensor()

    def read_internal_sensor(self):
        return_value = 0
        while True:
                return_value = grovepi.dht(self.i2c_connector,0)[self.i]
                if not any(np.isnan([return_value])):
                    # no value is NaN
                    break
        return return_value

class VirtualSensor(SensorInterface):
    def __init__(self, name: str, type_name: str, connector: int, connector_types: Connectortype, min_value: int, max_value: int, datatype: str, unit: str, read_interval: int, notify_interval: Notifyinterval, notify_change_precision: int):
        if connector_types != Connectortype.Virtual:
            raise ValueError("connector_type is not Digital.")
        super().__init__(name=name, type_name=type_name, connector=connector, connector_types=connector_types, min_value=min_value, max_value=max_value, datatype=datatype, unit=unit, read_interval=read_interval, notify_interval=notify_interval, notify_change_precision=notify_change_precision)
        #self.rng = np.random.default_rng(seed = self.i2c_connector) #doas not work on pi
        _ = self.read_sensor()

    def read_internal_sensor(self):
        mean = (self.min_value + self.max_value) / 2.0
        deviation = self.notify_change_precision / 2.0
        alpha = 0.5
        #random_change = self.rng.normal(loc = mean, scale = deviation)
        random_change = np.random.normal(loc = mean, scale = deviation)
        return self.last_value + alpha * (random_change - self.last_value)
