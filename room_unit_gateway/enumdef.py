from enum import Enum

class Connectortype(Enum):
    Analog = 1
    Digital = 2
    Digital_multiple_0 = 3
    Digital_multiple_1 = 4
    I2C_display = 5

class Notifyinterval(Enum):
    on_read = 1 # send a value every time the value is read independent of the notify_change_precision
    on_change = 2 # send a value every time the value changes more than notify_change_precision
    on_change_timeout = 2 # send a value every time the value changes more than notify_change_precision and after n reads
    on_rising_edge = 3 # send a value every time the value increases more thean notify_change_precision
    on_falling_edge = 4 # send a value every time the value decreases more thean notify_change_precision
    on_change_stable = 5 # send a value every time the value changes more than notify_change_precision and then wait untile it does no longer fluctuate
    on_rising_edge_stable = 6 # send a value every time the value increases more thean notify_change_precision and then wait untile it does no longer fluctuate
    on_falling_edge_stable = 7 # send a value every time the value decreases more thean notify_change_precision and then wait untile it does no longer fluctuate
    on_change_stable_timeout = 5 # send a value every time the value changes more than notify_change_precision and then wait untile it does no longer fluctuate and after n reads
    on_rising_edge_stable_timeout = 6 # send a value every time the value increases more thean notify_change_precision and then wait untile it does no longer fluctuate and after n reads
    on_falling_edge_stable_timeout = 7 # send a value every time the value decreases more thean notify_change_precision and then wait untile it does no longer fluctuate and after n reads