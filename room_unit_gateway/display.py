#!/usr/bin/env python

import grovepi
from grove_rgb_lcd import *

from enumdef import Connectortype

class Display:
    def __init__(self, id: int, name: str, display_type: str, i2c: int, i2c_type: Connectortype, initial_value: int):
        self.id = id #assert unique
        self.name = name
        self.type = display_type
        self.i2c_connector = i2c #assert not used twice
        self.connector_type = i2c_type
        self.last_value = initial_value
        grovepi.setRGB(0,255,0)
        self.write_display(initial_value)

    def __del__(self):
        grovepi.setRGB(0,0,0)
        grovepi.setText("")

    def __str__(self):
        return f"ID:{self.id},Name:{self.name},Type:{self.type},I2C:{self.i2c_connector},{self.connector_type},last value:{self.last_value}"
    
    def write_display(self, value: str):
        if len(value) > 20:
            raise ValueError("Test is too long")
        grovepi.setText(value)
        self.last_value = value
        print ("{}: {}".format(self.name,self.last_value))
