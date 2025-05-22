# Docker README

## initialisation
### server
- navgate to SCIoT_G02_2025
- docker-compose up

### pi room
- make sure ssh and I2C are allowed in the configurations of the pi
- configure room_unit_gateway/config.ini for the current hardware setting
- docker build -t room_pi - < pi.Dockerfile

## other usefull comands
docker-compose ps