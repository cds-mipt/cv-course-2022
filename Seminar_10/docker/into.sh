#!/bin/bash

docker exec --user "docker_carla" -it carla \
        /bin/bash -c ". /ros_entrypoint.sh; cd /home/docker_carla; /bin/bash"
