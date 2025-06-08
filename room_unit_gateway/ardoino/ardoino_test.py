import serial as serial
import time

message_end_signal = b''

def loop(ardoino_serial):
    val = 10
    try:
        while True:
            val = input("Enter a number: ") # Taking input from user 
            ardoino_serial.write(b's:' + str(val).encode() + b'\n')
            time.sleep(1)
            data = "Start"
            while(data != message_end_signal):
                data = ardoino_serial.readline()
                print (data)
    except KeyboardInterrupt:
        print("Stopping")
        ardoino_serial.close()

def main():
    ardoino_serial = serial.Serial('COM6', 9600, timeout=1)
    time.sleep(2)
    loop(ardoino_serial)

if __name__ == '__main__':
    main()