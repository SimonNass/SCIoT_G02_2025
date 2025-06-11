# TODO

- Define API interfaces
- pi
    - update python version in docker for room pi
    - check if ardoino as part of the pi works
    - test pi with no / wrong sensors, pi check that with nothing conneted or connected wrong it stil works
    - button add buffer to not send multiple messages if 
    - send welkome message for display
    - automatic discovery
- build an overview UI
- build DB
  - metadata
  - history state
  - current state?
- build aggregations and context information
- build planing AI
- send notes of lecture

## Meeting 27.05

- [X] Communication gateway -> backend (MQTT)
- [ ] Communication backend->gateway (MQTT)
- [X] Making motor work
- [] AI Planning
  - [X] Overarching Goals
  - [ ] Conversion of DB values to inital state
  - [X] First attempts at lecture implementation
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
