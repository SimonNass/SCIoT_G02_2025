import serial as serial
import serial.tools.list_ports
import time

def find_serial_port():
    ports = serial.tools.list_ports.comports()
    for p in ports:
        print(p.device)
    print(len(ports), 'ports found')
    return (str(p.device) for p in ports)



def remote_call(ardoino_serial: serial, message_end_signal: str, type_name: str, value):
    try:
        request_str = str(type_name).encode() + b':' + str(value).encode() + b'\n'
        #print("Request > {} \n".format(request_str))
        ardoino_serial.write(request_str)
        time.sleep(1)
        data = b'Start'
        while (data.decode('utf-8').strip() != message_end_signal):
            data = ardoino_serial.readline()
            print (data.decode('utf-8').strip())
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
    usb_channel_type = find_serial_port()[0]
    usb_channel_data_rate = 9600
    # in bps
    ardoino_serial = serial.Serial(usb_channel_type, usb_channel_data_rate, timeout=1)
    time.sleep(2)
    loop(ardoino_serial,message_end_signal)
    ardoino_serial.close()

if __name__ == '__main__':
    main()