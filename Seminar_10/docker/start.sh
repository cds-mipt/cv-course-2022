#!/bin/bash

orange=`tput setaf 3`
reset_color=`tput sgr0`

export ARCH=`uname -m`

echo "Running on ${orange}${ARCH}${reset_color}"

if [ "$ARCH" == "x86_64" ] 
then
    ARGS="--ipc host --gpus all -e NVIDIA_DRIVER_CAPABILITIES=all"
else
    echo "Arch ${ARCH} not supported"
    exit
fi

xhost +local:root
docker run -itd --rm \
        $ARGS \
        --env="DISPLAY=$DISPLAY" \
        --env="QT_X11_NO_MITSHM=1" \
        --privileged \
        --name carla \
        --net "host" \
        -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
        -v ${CARLA_ROOT}:/home/docker_carla/carla:rw \
        -v /home/${USER}:/home/${USER}:rw \
        ${ARCH}melodic/carla:${CARLA_VERSION} \
        /bin/bash 
