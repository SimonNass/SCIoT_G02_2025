#!/usr/bin/env python

try:
    import grovepi
    from grove_rgb_lcd import *
except ImportError:
    grovepi = None
    grove_rgb_lcd = None
import time
import logging
logger = logging.getLogger(__name__)

from enumdef import Connectortype
from actuators.actuator import ActuatorInterface

class DisplayActuator(ActuatorInterface):
    def __init__(self, name: str, type_name: str, connector: int, connector_types: Connectortype, min_value: str, max_value: str, datatype: str, unit: str, initial_value: str, off_value: str):
        if connector_types != Connectortype.I2C_display:
            raise ValueError("Connector_type is not Analog.")
        super().__init__(name=name,type_name=type_name,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value,datatype=datatype,unit=unit,initial_value=initial_value,off_value=off_value)
        self.char_limit = 16 * 2
        split = self.initial_value.split(",")
        r = int(split[0])
        g = int(split[1])
        b = int(split[2])
        text = split[3]
        try:
            setRGB(r,g,b)
        except  (Exception, AttributeError) as e:
            print ("setRGB was unsucesful")
            #print (e)
            logger.error("{}: setRGB was unsucesful {}".format(self.name, e))
        self.write_actuator(text)

    def __del__(self):
        split = self.off_value.split(",")
        r = int(split[0])
        g = int(split[1])
        b = int(split[2])
        text = split[3]
        try:
            setText(text)
            setRGB(r,g,b)
        except  (Exception, AttributeError) as e:
            print ("setRGB or setText was unsucesful")
            #print (e)
            logger.error("{}: setRGB or setText was unsucesful {}".format(self.name, e))

    def write_actuator(self, value: str):
        write_value = value
        try:
            if len(write_value) > self.char_limit:
                print ("Text is too long")
                #raise ValueError("Text is too long")
                write_value = write_value[:self.char_limit]
            _ = self.write_internal_actuator(write_value)
            self.last_value_timestamp = time.time()
            self.last_value = write_value
            self.datatype = str(type(self.last_value))
            print ("{}: {}".format(self.name,self.last_value))
            logger.info("{}: {} {}".format(self.name,self.last_value, self.datatype))
        except Exception as e:
            print ("write was unsucesful")
            #print (e)
            logger.error("{}: write was unsucesful {}".format(self.name, e))
    
    def write_internal_actuator(self, write_value: str):
        setText(write_value)
        return 1
