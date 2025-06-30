# SCIoT_G02_2025
Smart City and IoT project of group 02

### Setup
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