# TODO

- Define API interfaces and MQTT topology
- make docker components talk to each other
- pi
    - update python version in docker for room pi
    - get the motor working
    - test pi with no / wrong sensors, pi check that with nothing conneted or connected wrong it stil works
    - send maxi example actuator request and response
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

- [ ] Communication gateway -> backend (MQTT)
- [ ] Communication backend->gateway (MQTT)
- [ ] Making motor work
- [ ] AI Planning
  - [ ] Overarching Goals
  - [ ] Conversion of DB values to inital state
  - [ ] First attempts at lecture implementation
- [ ] Frontend
  - [ ] Needed Backend Endpoints
- [ ] Simulation
  - [ ] Decide on simulator (needs to provide data via MQTT)



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
