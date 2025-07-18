# TODO

- [ ] (Simon) send notes of lecture

- [x] Communication gateway -> backend (MQTT)
- [x] Communication backend->gateway (MQTT)
- [x] Making motor work
- [ ] Gateway
  - [x] (Simon) sensor dictionary send in utf 8
  - [x] (Simon) send bool actuator is off or on in gateway info
  - [ ] (Simon) test send after actuator change
  - [ ] (Simon) make agregated sensor subclass that cumulates sensors when read !!!!!!
  - [x] (Simon) disable sensors ? > not needed just ignore them
  - [ ] (optional) (Simon) update random number generator manual list
  - [ ] (optional) (Simon) Toggle button sensor?
  - [ ] (optional) (Simon) send welkome message for display
  - [ ] (optional) (Simon) button add buffer to not send multiple messages if
  - [ ] (optional) (Simon) test pi with no / wrong sensors, pi check that with nothing conneted or connected wrong it stil works
  - [ ] (optional) (Simon) update python version in docker for room pi
  - [x] (Simon) add ai planing increrase decrease to actuators
  - [x] (Simon) add ai planing types to IoT
  - [ ] (optional) (Simon) rename ardoino to arduino
  - [x] (Simon) actuators "min":"0", "max":"32"
  - [x] (Simon) mapping firtual environment toggle for real sensor actuator paar
  - [x] (Simon) send firtual environment formating
  - [x] bug when broker not connected ?bug no longer apeares
  - [x] ardoino sensor return prefix needs to be removed
  - [x] send ardoino values not 0 to mqtt broker

- [ ] AI Planning
  - [x] Overarching Goals
  - [x] (Simon) Activity recognition in ai planer or in context generation
  - [x] First attempts at lecture implementation
  - [x] (Simon) plan cleaning and do not plan cleaning toggle
  - [x] (Simon) mapping in pddl a -> s
  - [ ] (Simon) Actuator_Text teg
  - [ ] (optional) (Simon) individual sensor goals
  - [ ] (optional) (Simon) room positiones
  - [ ] (Simon) program activitys in config file
  - [ ] (optional) (Maximilian, Simon) Sensor aggregation

- [ ] Frontend
 - [ ] actuators display off or on
 - [ ] set actuator value from frontend

- [ ] backend
  - [ ] Needed Backend Endpoints
  - [x] (Maximilian) Conversion of DB values to context to inital state
  - [x] (Maximilian) mapping ifrom db to pddl a -> s
  - [x] (Maximilian) provide actuator active/inactive value (need value from frontend)
  - [x] (Maximilian) Set room occupancy endpoint
  - [x] (Maximilian) Get Config values
  - [x] (Maximilian) Set Config values
  - [ ] (Maximilian) Start AI Planning for list of rooms (check with database values and thresholds to create problem)
  - [x] Endpoint to change any actuator value
  - [x] (Maximilian) Add lastest values as normal and simplified value to list_devices_in_room
  - [x] (Maximilian) (optional) Endpoint to provide values and simplified values across a certain timespan
  - [x] (Maximilian) Endpoint that provides the plan
  - [x] convert sensor values to high ok low
  - [x] Add endpoint to manually delete devices last seen more than x-minutes ago


- [x] Simulation
  - [x] Decide on simulator (needs to provide data via MQTT)
  - [ ] update config files to newest form

- [] Bugs 
  - [x] (Simon, Maximilian) Bug: "°C", degree Symbol not being parsed correctly in mqtt incoming message -> May need to be parsed on the frontend -> solvet on gateway?

# AI planing tools

- editor.planing.domains https://editor.planning.domains/#
- vsual studio code extension PDDL etension for Visual Studio Code

ai planer of schelf
fast Forward ff
metric-ff (+ nummeric planers)
ff-x
conformant-ff
configent-ff
FD

solver.planing.domains https://solver.planning.domains/ with POST request
PDDL VS code extension (+ test cases)
FF https://fai.cs.uni-saarland.de/hoffmann/ff.html
JavaFF
FD https://planning.wiki/ref/planners/fd
