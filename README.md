# SCIoT_G02_2025
Smart City and IoT project of group 02

### Setup

#### Backend

To inizilaize the docker-compose file correctly, which will start both the Bckend, Mqtt-Broker and the AI-Planner you first need to build the Dockerfile with the following command:
```
$ docker build -t paas:latest .
``` 
Afterwards you can run the Docker-Compose file, assuming that you have created a `.env` file (use `.env.example` as a template), with the following command:
```
$ docker-compose up --build
``` 
This should startup all docker containers correctly.
This will fail if you already have any other services running on host ports that are not listed in the `docker-compose` file. These ports include, but are not limited to: 80, 5001, 5555 etc..
<br/>
You can also increase the amount of AI-Planning workers available to calculate plans like this:
```
$ docker compose up -d --scale worker=5 --no-recreate
```
In this case 5 workers will be created, each capable of accepting individual tasks. Task orchestration between the workers is handeld automatically.

#### Frontend

To start the frontend execute the following comand:
```bash
$ python3 .\frontend\main.py
```
In the web page then switch to the admin pannel:

#### IoT

To start the IoT, gateway, ... on the pi 
```bash
$ sudo docker build --tag 'room-pi' -f pi.Dockerfile .
$ sudo docker run --privileged --network host room-pi
```

for controle over host config file and host:
```bash
sudo docker run --privileged --network host room-pi "configs_dir/config.ini" "host" "password"
```

#### debugging

the ai planing file creation can also be triggered manually
```bash
.\test_and_present_single_components.py True .\backend\aiplaning\config\ai_planer_test_example.ini False
```
