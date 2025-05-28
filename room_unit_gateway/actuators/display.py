#!/usr/bin/env python

import grovepi
from grove_rgb_lcd import *
import uuid

from enumdef import Connectortype

class Display:
    def __init__(self, name: str, type_name: str, connector: int, connector_types: Connectortype, min_value: str, max_value: str, datatype: str, unit: str, initial_value: str, off_value: str):
        self.id = uuid.uuid1()
        self.name = name
        self.type = type_name
        self.i2c_connector = connector #assert not used twice
        self.connector_type = connector_types
        self.last_value = initial_value
        self.char_limit = 16 * 2
        setRGB(0,255,0)
        self.write_display(initial_value)

    def __del__(self):
        setText("")
        setRGB(0,0,0)

    def __str__(self):
        return "ID:{},Name:{},Type:{},I2C:{},{},last value:{}".format(self.id,self.name,self.type,self.i2c_connector,self.connector_type,self.last_value)

    def __dict__(self):
        return {"id":self.id,"name":self.name,"type":self.type,"i2c":self.i2c_connector,"connector_type":self.connector_type,"last_value":self.last_value}

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
        except Exception as e:
            print ("write was unsucesful")
            print (e)
