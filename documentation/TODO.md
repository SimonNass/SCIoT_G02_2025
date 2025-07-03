# TODO

- pi
  - update python version in docker for room pi
  - test pi with no / wrong sensors, pi check that with nothing conneted or connected wrong it stil works
  - button add buffer to not send multiple messages if
  - send welkome message for display
- build aggregations and context information
- build planing AI
- send notes of lecture

## Meeting 01.07

- [x] Communication gateway -> backend (MQTT)
- [X] Communication backend->gateway (MQTT)
- [x] Making motor work
- [ ] Gateway
  - (Simon) [] sensor dictionary send in utf 8
  - [ ] send bool acxtuator is off or on in gateway info
  - [ ] disable sensors ?
  - [ ] update random number generator manual list

- [ ] AI Planning
  - [x] Overarching Goals
  - [ ] Conversion of DB values to context to inital state
  - [ ] Activity recognition
  - [x] First attempts at lecture implementation
  - [plan cleaning and do not plan cleaning toggle]
  - [ ] mapping in pddl a -> s

- [ ] Frontend
 - [ ] actuators off or on
 - [ ] set actuator value from frontend

- [ ] backend
  - [ ] Needed Backend Endpoints
  - [ ] (Maximilian) provide actuator active/inactive value (need value from frontend)
  - [ ] (Maximilian) Set room occupancy endpoint
  - [ ] (Maximilian) Get Config values
  - [ ] (Maximilian) Set Config values
  - [ ] (Maximilian) Start AI Planning for list of rooms (check with database values and thresholds to create problem)
  - [x] Endpoint to change any actuator value
  - [ ] (Maximilian) Add lastest values as normal and simplified value to list_devices_in_room
  - [ ] (Maximilian) (optional) Endpoint to provide values and simplified values across a certain timespan
  - [ ] (Maximilian) Endpoint that provides the plan
  - [ ] convert sensor values to high ok low


- [x] Simulation
  - [x] Decide on simulator (needs to provide data via MQTT)

- [] Bugs - [ ] (Simon, Maximilian) Bug: "°C", degree Symbol not being parsed correctly in mqtt incoming message -> May need to be parsed on the frontend

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
