import serial as serial
import time
import logging
logger = logging.getLogger(__name__)

from sensors.sensor import SensorInterface
from actuators.actuator import ActuatorInterface
from enumdef import Connectortype, Notifyinterval


class ArdoinoSensor(SensorInterface):
    def __init__(self, name: str, type_name: str, connector: int, connector_types: Connectortype, min_value: int, max_value: int, datatype: str, unit: str, read_interval: int, notify_interval: Notifyinterval, notify_change_precision: int, message_end_signal: str, usb_channel_type: str, usb_channel_data_rate: int):
        if connector_types != Connectortype.Analog:
            raise ValueError("Connector_type is not Analog.")
        super().__init__(name=name, type_name=type_name, connector=connector, connector_types=connector_types, min_value=min_value, max_value=max_value, datatype=datatype, unit=unit, read_interval=read_interval, notify_interval=notify_interval, notify_change_precision=notify_change_precision)
        self.message_end_signal = message_end_signal
        self.usb_channel_type = usb_channel_type
        self.usb_channel_data_rate = usb_channel_data_rate
        self.type_name = "temperature"
        # in bps
        self.ardoino_serial = serial.Serial(self.usb_channel_type, self.usb_channel_data_rate, timeout=1)
        time.sleep(2)
        _ = self.read_sensor()

    def __del__(self):
        try:
            self.ardoino_serial.close()
        except (Exception, IOError, TypeError, AttributeError) as e:
            print ("closing ardoino_serial was unsucesful")
            #print (e)
            logger.info("closing ardoino_serial was unsucesful {}".format(e))

    def read_internal_sensor(self):
        remote_call(self.ardoino_serial, self.message_end_signal, self.type_name, 0)
        return 0

class ArdoinoActuator(ActuatorInterface):
    def __init__(self, name: str, type_name: str, connector: int, connector_types: Connectortype, min_value: int, max_value: int, datatype: str, unit: str, initial_value: int, off_value: int, message_end_signal: str, usb_channel_type: str, usb_channel_data_rate: int):
        if connector_types != Connectortype.Analog:
            raise ValueError("Connector_type is not Analog.")
        super().__init__(name=name,type_name=type_name,connector=connector,connector_types=connector_types,min_value=min_value,max_value=max_value,datatype=datatype,unit=unit,initial_value=initial_value,off_value=off_value)
        self.message_end_signal = message_end_signal
        self.usb_channel_type = usb_channel_type
        self.usb_channel_data_rate = usb_channel_data_rate
        self.type_name = "motor"
        # in bps
        self.ardoino_serial = serial.Serial(self.usb_channel_type, self.usb_channel_data_rate, timeout=1)
        time.sleep(2)
        self.write_actuator(self.initial_value)

    def __del__(self):
        try:
            self.ardoino_serial.close()
        except (Exception, IOError, TypeError, AttributeError) as e:
            print ("closing ardoino_serial was unsucesful")
            #print (e)
            logger.info("closing ardoino_serial was unsucesful {}".format(e))

    def write_internal_actuator(self, write_value: int):
        remote_call(self.ardoino_serial, self.message_end_signal, self.type_name, write_value)
        return 0

def remote_call(ardoino_serial: serial, message_end_signal: str, type_name: str, value):
    try:
        request_str = str(type_name).encode() + b':' + str(value).encode() + b'\n'
        #print("Request > {} \n".format(request_str))
        ardoino_serial.write(request_str)
        time.sleep(1)
        data = "Start"
        while(data != str(message_end_signal).encode()):
            data = ardoino_serial.readline()
            print (data)
    except (Exception, KeyboardInterrupt) as e:
        print("Stopping")
        print(e)
        ardoino_serial.close()

def loop(ardoino_serial,message_end_signal: str):
    try:
        while True:
            # Taking input from user 
            type_name = input("Enter a sensor / actuator: ")
            # options: motor soundlevel humidity temperature rfid exit
            # TODO what if anything els gets entered?
            value = input("Enter a number: ")
            remote_call(ardoino_serial,message_end_signal,type_name,value)
    except KeyboardInterrupt:
        print("Stopping")
        ardoino_serial.close()

def main():
    message_end_signal = ''
    usb_channel_type = 'COM6'
    usb_channel_data_rate = 9600
    # in bps
    ardoino_serial = serial.Serial(usb_channel_type, usb_channel_data_rate, timeout=1)
    time.sleep(2)
    loop(ardoino_serial,message_end_signal)
    ardoino_serial.close()

if __name__ == '__main__':
    main()