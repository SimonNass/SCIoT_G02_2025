#!/usr/bin/env python

import grovepi
from grove_rgb_lcd import *

from enumdef import Connectortype

class Display:
    def __init__(self, id: int, name: str, display_type: str, i2c: int, i2c_type: Connectortype, initial_value: str):
        self.id = id #assert unique
        self.name = name
        self.type = display_type
        self.i2c_connector = i2c #assert not used twice
        self.connector_type = i2c_type
        self.last_value = initial_value
        self.char_limit = 16 * 2
        setRGB(0,255,0)
        self.write_display(initial_value)

    def __del__(self):
        setRGB(0,0,0)
        setText("")

    def __str__(self):
        return "ID:{},Name:{},Type:{},I2C:{},{},last value:{}".format(self.id,self.name,self.type,self.i2c_connector,self.connector_type,self.last_value)

    def write_display(self, value: str):
        write_value = value
        try:
            if len(write_value) > self.char_limit:
                print ("Text is too long")
                #raise ValueError("Text is too long")
                write_value = write_value[:self.char_limit]
            setText(write_value)
            self.last_value = write_value
            print ("{}: {}".format(self.name,self.last_value))
        except:
            print ("write was unsucesful")
