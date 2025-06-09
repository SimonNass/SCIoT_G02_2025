import serial as serial
import time
import logging
logger = logging.getLogger(__name__)

class ArdoinoReverseProxy():
    def __init__(self, message_end_signal: str, usb_channel_type: str, usb_channel_data_rate: int):
        self.message_end_signal = message_end_signal
        self.usb_channel_type = usb_channel_type
        self.usb_channel_data_rate = usb_channel_data_rate
        # in bps
        self.ardoino_serial = serial.Serial(self.usb_channel_type, self.usb_channel_data_rate, timeout=1)
        time.sleep(2)

    def __del__(self):
        try:
            self.ardoino_serial.close()
        except (Exception, IOError, TypeError, AttributeError) as e:
            print ("closing ardoino_serial was unsucesful")
            #print (e)
            logger.info("closing ardoino_serial was unsucesful {}".format(e))
    
    def remote_call(self, type_name: str, value):
        try:
            request_str = str(type_name).encode() + b':' + str(value).encode() + b'\n'
            #print("Request > {} \n".format(request_str))
            self.ardoino_serial.write(request_str)
            time.sleep(1)
            data = "Start"
            while(data != str(self.message_end_signal).encode()):
                data = self.ardoino_serial.readline()
                print (data)
            return "result"
        except (Exception, KeyboardInterrupt) as e:
            print("Stopping")
            print(e)
            self.ardoino_serial.close()