# Gateway protocol

## separation northbound gateway
- IoT type
- device ID
- room ID
- timeout
- sensing intervals
- current value
- protocol version x:x:x:x

## separation southbound gateway
- IoT type
- IoT device subtype
- device ID
- timeout
- current value

## other differences
- binary vs range of values {(0,1,1), (min value, max value, step size, average/mean value, variation of values)}
- sensors vs actuators
- REST like GET, SET, POST (UPDATE), DELETE, HEAD (META DATA)
- Type of IoT (electronic, software, human, simulated, virtual)-based IoT
- simulated value generation (random increase and decrease, statistically based)
- simulated values (amount of devices, amount of rooms)


## IoT-based type sensors
- electronic 
    - card reader
    - light level
    - sound intensity
- software 
    - weather api
    - air quality api
    - electricity api
    - calender api
- human 
    - room based controler for optimal values
    - room modes (sleeping, reading, working, ...)
- simulated
    - heating
    - ventilation
    - water preasure
- virtual

## IoT-based type actuators
- electronic 
    - access card
    - light led
    - light blinds
    - speaker
- software 
- human 
    - send hotel employee to do something
- simulated 
    - air conditioning
    - window state
    - water gate
- virtual