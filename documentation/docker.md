# Docker README

## initialisation
### Backend Server
To inizilaize the docker-compose file correctly, which will start both the Bckend, Mqtt-Broker and the AI-Planner you first need to build the Dockerfile with the following command:
```
docker build -t paas:latest .
``` 
Afterwards you can run the Docker-Compose file, assuming that you have created a `.env` file (use `.env.example` as a template), with the following command:
```
docker-compose up --build
``` 
This should startup all docker containers correctly.
This will fail if you already have any other services running on host ports that are not listed in the `docker-compose` file. These ports include, but are not limited to: 80, 5001, 5555 etc..
<br/>
You can also increase the amount of AI-Planning workers available to calculate plans like this:
```
docker compose up -d --scale worker=5 --no-recreate
```
In this case 5 workers will be created, each capable of accepting individual tasks. Task orchestration between the workers is handeld automatically.

#### debug
docker-compose down --volumes --remove-orphans
docker system prune -af
docker-compose pull
docker-compose build
docker-compose up


### pi room
- make sure ssh and I2C are allowed in the configurations of the pi
- configure room_unit_gateway/config.ini for the current hardware setting
- docker build -t room_pi - < pi.Dockerfile

## other usefull comands
docker-compose ps

Install Docker on PI after this URL tutorial:
https://docs.docker.com/engine/install/raspberry-pi-os/
sudo docker build --tag 'room-pi' -f pi.Dockerfile .
sudo docker run --privileged --network host room-pi
sudo docker stop $(sudo docker ps -a -q)
docker system prune
