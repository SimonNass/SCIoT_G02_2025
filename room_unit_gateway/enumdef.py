from enum import Enum

class Connectortype(Enum):
    Analog = 1
    Digital = 2
    Digital_multiple_0 = 3
    Digital_multiple_1 = 4
    I2C_display = 5
    Virtual = 6
    Ardoino_temperature = 7
    Ardoino_humidity = 8
    Ardoino_soundlevel = 9
    Ardoino_rfid = 10
    Ardoino_motor = 11
    # TODO make x_y mapping not with enums but in the generation itself

class Notifyinterval(Enum):
    on_read = 1 # send a value every time the value is read independent of the notify_change_precision
    on_change = 2 # send a value every time the value changes more than notify_change_precision
    on_change_timeout = 3 # send a value every time the value changes more than notify_change_precision and after n reads
    on_rising_edge = 4 # send a value every time the value increases more thean notify_change_precision
    on_falling_edge = 5 # send a value every time the value decreases more thean notify_change_precision
    on_change_stable = 6 # send a value every time the value changes more than notify_change_precision and then wait untile it does no longer fluctuate
    on_rising_edge_stable = 7 # send a value every time the value increases more thean notify_change_precision and then wait untile it does no longer fluctuate
    on_falling_edge_stable = 8 # send a value every time the value decreases more thean notify_change_precision and then wait untile it does no longer fluctuate
    on_change_stable_timeout = 9 # send a value every time the value changes more than notify_change_precision and then wait untile it does no longer fluctuate and after n reads
    on_rising_edge_stable_timeout = 10 # send a value every time the value increases more thean notify_change_precision and then wait untile it does no longer fluctuate and after n reads
    on_falling_edge_stable_timeout = 11 # send a value every time the value decreases more thean notify_change_precision and then wait untile it does no longer fluctuate and after n reads