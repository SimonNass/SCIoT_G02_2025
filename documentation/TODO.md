# TODO

- Define API interfaces
- pi
  - update python version in docker for room pi
  - test pi with no / wrong sensors, pi check that with nothing conneted or connected wrong it stil works
  - button add buffer to not send multiple messages if
  - send welkome message for display
- build an overview UI
- build DB
  - metadata
  - history state
  - current state?
- build aggregations and context information
- build planing AI
- send notes of lecture

## Meeting 27.05

- [x] Communication gateway -> backend (MQTT)
- [x] Communication backend->gateway (MQTT)
- [x] Making motor work
- [ ] AI Planning
  - [x] Overarching Goals
  - [ ] Conversion of DB values to context to inital state
  - [x] First attempts at lecture implementation
- [ ] Frontend

- [ ] Needed Backend Endpoints
  - [ ] (Maximilian) provide actuator active/inactive value (need value from frontend)
  - [x] (Maximilian) Set room occupancy endpoint
  - [x] (Maximilian) Get Config values
  - [x] (Maximilian) Set Config values
  - [ ] (Maximilian) Start AI Planning for list of rooms (check with database values and thresholds to create problem)
  - [x] Endpoint to change any actuator value
  - [x] (Maximilian) Add lastest values as normal and simplified value to list_devices_in_room
  - [ ] (Maximilian) (optional) Endpoint to provide values and simplified values across a certain timespan
  - [ ] (Maximilian) Endpoint that provides the plan

- [x] Simulation

  - [x] Decide on simulator (needs to provide data via MQTT)

- [ ] Bugs 
  - [ ] (Simon, Maximilian) Bug: "°C", degree Symbol not being parsed correctly in mqtt incoming message -> May need to be parsed on the frontend

ai planing tools

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
