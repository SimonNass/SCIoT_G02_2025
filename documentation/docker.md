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

Install Docker on PI after this URL tutorial:
https://docs.docker.com/engine/install/raspberry-pi-os/
sudo docker build --tag 'room-pi' -f pi.Dockerfile .
sudo docker run --privileged room-pi
sudo docker stop $(sudo docker ps -a -q)
docker system prune
