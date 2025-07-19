#!/usr/bin/env python
"""Module specifies the sensors."""

try:
    import grovepi
    from grovepi import *
except ImportError:
    grovepi = None
from abc import ABC, abstractmethod
import logging
import time
import numpy as np
import random_number_generator as rng
from enumdef import Connectortype, Notifyinterval
from iot_info import IoT_Info
logger = logging.getLogger(__name__)

class SensorInterface(ABC):
    def __init__(self, general_iot_device: IoT_Info, read_interval: int, notify_interval: Notifyinterval, notify_change_precision: int):
        self.general_iot_device = general_iot_device
        self.read_interval = read_interval
        self.notify_interval = notify_interval
        self.notify_change_precision = notify_change_precision
        self.last_value = self.general_iot_device.min_value
        self.last_value_timestamp = time.time()
        self.virtual_environment_impact = 0

    def __str__(self):
        return str(self.__dict__())

    def __dict__(self):
        return_dict = {}
        return_dict.update(self.general_iot_device.__dict__())
        return_dict.update({"read_interval":self.read_interval, "notify_interval":str(self.notify_interval), "notify_change_precision":self.notify_change_precision, "last_value":self.last_value})
        return return_dict

    def read_sensor(self):
        try:
            roaw_sensor_value = self.read_internal_sensor()
            manipulated_sensor_value = roaw_sensor_value + self.virtual_environment_impact
            self.last_value = max(self.general_iot_device.min_value,min(self.general_iot_device.max_value,manipulated_sensor_value))
            self.last_value_timestamp = time.time()
            self.datatype = str(type(self.last_value))
            print (f"uuid: {self.general_iot_device.id}, device name: {self.general_iot_device.name}, value: {self.last_value} = {roaw_sensor_value} + {self.virtual_environment_impact}")
            logger.info(f"uuid: {self.general_iot_device.id}, device name: {self.general_iot_device.name}, value: {self.last_value} = {roaw_sensor_value} + {self.virtual_environment_impact}, type: {self.datatype}")
            return self.__dict__()
        except (Exception, IOError, TypeError) as e:
            print ("read was unsucesful")
            #print (e)
            logger.error(f"{self.general_iot_device.name}: read was unsucesful {e}")
            raise e

    def write_sensor(self, value: float):
        try:
            roaw_sensor_value = float(value)
            manipulated_sensor_value = roaw_sensor_value + self.virtual_environment_impact
            self.last_value = max(self.general_iot_device.min_value,min(self.general_iot_device.max_value,manipulated_sensor_value))
            self.last_value_timestamp = time.time()
            self.datatype = str(type(self.last_value))
            print (f"uuid: {self.general_iot_device.id}, device name: {self.general_iot_device.name}, value: {self.last_value} = {roaw_sensor_value} + {self.virtual_environment_impact}")
            logger.info(f"uuid: {self.general_iot_device.id}, device name: {self.general_iot_device.name}, value: {self.last_value} = {roaw_sensor_value} + {self.virtual_environment_impact}, type: {self.datatype}")
            return self.__dict__()
        except (Exception, IOError, TypeError) as e:
            print ("write was unsucesful")
            #print (e)
            logger.error(f"{self.general_iot_device.name}: write was unsucesful {e}")
            raise e

    @abstractmethod
    def read_internal_sensor(self):
        pass

class AnalogSensor(SensorInterface):
    def __init__(self, general_iot_device: IoT_Info, read_interval: int, notify_interval: Notifyinterval, notify_change_precision: int):
        if general_iot_device.connector_type != Connectortype.Analog:
            raise ValueError("Connector_type is not Analog.")
        super().__init__(general_iot_device=general_iot_device, read_interval=read_interval, notify_interval=notify_interval, notify_change_precision=notify_change_precision)
        _ = self.read_sensor()

    def read_internal_sensor(self):
        return grovepi.analogRead(self.general_iot_device.i2c_connector)

class DigitalSensor(SensorInterface):
    def __init__(self, general_iot_device: IoT_Info, read_interval: int, notify_interval: Notifyinterval, notify_change_precision: int):
        if general_iot_device.connector_type != Connectortype.Digital:
            raise ValueError("connector_type is not Digital.")
        super().__init__(general_iot_device=general_iot_device, read_interval=read_interval, notify_interval=notify_interval, notify_change_precision=notify_change_precision)
        try:
            grovepi.pinMode(self.general_iot_device.i2c_connector,"INPUT")
        except  AttributeError as e:
            print ("pinMode was unsucesful")
            #print (e)
            logger.error(f"{self.general_iot_device.name}: pinMode was unsucesful {e}")
        _ = self.read_sensor()

    def read_internal_sensor(self):
        return grovepi.digitalRead(self.general_iot_device.i2c_connector)

class DigitalMultipleSensor(SensorInterface):
    def __init__(self, general_iot_device: IoT_Info, read_interval: int, notify_interval: Notifyinterval, notify_change_precision: int, i: int):
        if general_iot_device.connector_type not in [Connectortype.Digital_multiple_0, Connectortype.Digital_multiple_1]:
            raise ValueError("connector_type is not Digital_multiple.")
        super().__init__(general_iot_device=general_iot_device, read_interval=read_interval, notify_interval=notify_interval, notify_change_precision=notify_change_precision)
        self.i = i
        try:
            grovepi.pinMode(self.general_iot_device.i2c_connector,"INPUT")
        except  AttributeError as e:
            print ("pinMode was unsucesful")
            #print (e)
            logger.error(f"{self.general_iot_device.name}: pinMode was unsucesful {e}")
        _ = self.read_sensor()

    def read_internal_sensor(self):
        return_value = 0
        while True:
            return_value = grovepi.dht(self.general_iot_device.i2c_connector,0)[self.i]
            if not any(np.isnan([return_value])):
                # no value is NaN
                break
        return return_value

class VirtualSensor_numerical(SensorInterface):
    def __init__(self, general_iot_device: IoT_Info, read_interval: int, notify_interval: Notifyinterval, notify_change_precision: int):
        if general_iot_device.connector_type != Connectortype.Virtual_numerical:
            raise ValueError("connector_type is not Digital.")
        super().__init__(general_iot_device=general_iot_device, read_interval=read_interval, notify_interval=notify_interval, notify_change_precision=notify_change_precision)
        self.rng_selector = 5
        self.seed = 0
        self.index = 0
        self.next_decrease = False
        _ = self.read_sensor()

    def read_internal_sensor(self):
        value = self.last_value
        if self.rng_selector == 0:
            value = rng.constant(last_value=self.last_value, min_value=self.general_iot_device.min_value, max_value=self.general_iot_device.max_value)
        elif self.rng_selector == 1:
            value = rng.simple_random(min_value=self.general_iot_device.min_value, max_value=self.general_iot_device.max_value)
        elif self.rng_selector == 2:
            value = rng.binary_random()
        elif self.rng_selector == 3:
            value = rng.complex_random(min_value=self.general_iot_device.min_value, max_value=self.general_iot_device.max_value, precision= self.notify_change_precision)
        elif self.rng_selector == 4:
            value, self.next_decrease = rng.bounce_random(last_value=self.last_value, min_value=self.general_iot_device.min_value, max_value=self.general_iot_device.max_value, precision=self.notify_change_precision, alpha=0.5, decrease=self.next_decrease)
        elif self.rng_selector == 5:
            value = rng.random_value(last_value=self.last_value, min_value=self.general_iot_device.min_value, max_value=self.general_iot_device.max_value, precision= self.notify_change_precision, alpha=0.5)
        elif self.rng_selector == 6:
            value = rng.predefined_sequence(min_value=self.general_iot_device.min_value, max_value=self.general_iot_device.max_value, seed=self.seed, index=self.index)
            self.index = self.index + 1
        else:
            # defoult
            value = rng.random_value(last_value=self.last_value, min_value=self.general_iot_device.min_value, max_value=self.general_iot_device.max_value, precision= self.notify_change_precision, alpha=0.5)
        return value

class VirtualSensor_binary(SensorInterface):
    def __init__(self, general_iot_device: IoT_Info, read_interval: int, notify_interval: Notifyinterval, notify_change_precision: int):
        if general_iot_device.connector_type != Connectortype.Virtual_binary:
            raise ValueError("connector_type is not Digital.")
        super().__init__(general_iot_device=general_iot_device, read_interval=read_interval, notify_interval=notify_interval, notify_change_precision=1)
        _ = self.read_sensor()

    def read_internal_sensor(self):
        value = rng.binary_random()
        return value
