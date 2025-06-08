import serial as serial
import time

def loop(ardoino_serial):
    val = 10
    try:
        while True:
            ardoino_serial.write(b's:' + str(val).encode() + b'\n')
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping")
        ardoino_serial.close()

def main():
    ardoino_serial = serial.Serial('COM6', 9600, timeout=1)
    time.sleep(2)
    loop(ardoino_serial)

if __name__ == '__main__':
    main()