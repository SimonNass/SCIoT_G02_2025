#!/usr/bin/env python

import grovepi
from grove_rgb_lcd import *
import uuid

from enumdef import Connectortype
from actuators.actuator import ActuatorInterface

class DisplayActuator(ActuatorInterface):
    def __init__(self, name: str, type_name: str, connector: int, connector_types: Connectortype, min_value: str, max_value: str, datatype: str, unit: str, initial_value: str, off_value: str):
        if connector_types != Connectortype.I2C_display:
            raise ValueError("Connector_type is not Analog.")
        super().__init__(name=name,type_name=type_name,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value,datatype=datatype,unit=unit,initial_value=initial_value,off_value=off_value)
        self.char_limit = 16 * 2
        split = self.initial_value.split(",")
        r = split[0]
        g = split[1]
        b = split[2]
        text = split[3]
        setRGB(r,g,b)
        self.write_display(text)

    def __del__(self):
        split = self.off_value.split(",")
        r = split[0]
        g = split[1]
        b = split[2]
        text = split[3]
        setText(text)
        setRGB(r,g,b)

    def write_actuator(self, value: str):
        write_value = value
        try:
            if len(write_value) > self.char_limit:
                print ("Text is too long")
                #raise ValueError("Text is too long")
                write_value = write_value[:self.char_limit]
            setText(write_value)
            self.last_value = write_value
            print ("{}: {}".format(self.name,self.last_value))
        except Exception as e:
            print ("write was unsucesful")
            print (e)
