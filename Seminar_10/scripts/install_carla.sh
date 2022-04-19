#!/bin/bash

orange=`tput setaf 3`
reset_color=`tput sgr0`

echo "${orange}Installing CARLA ${CARLA_VERSION} to ${CARLA_ROOT}...${reset_color}"

mkdir ${CARLA_ROOT} -p && cd ${CARLA_ROOT}

echo "${orange}Downloading CARLA and AdditionalMaps...${reset_color}"
wget -c https://carla-releases.s3.eu-west-3.amazonaws.com/Linux/CARLA_${CARLA_VERSION}.tar.gz
wget -c https://carla-releases.s3.eu-west-3.amazonaws.com/Linux/AdditionalMaps_${CARLA_VERSION}.tar.gz

echo "${orange}Extracting CARLA...${reset_color}"
mkdir CARLA_${CARLA_VERSION}
tar -xvf CARLA_${CARLA_VERSION}.tar.gz --directory CARLA_${CARLA_VERSION}

echo "${orange}Importing AdditionalMaps...${reset_color}"
mv ${CARLA_ROOT}/AdditionalMaps_${CARLA_VERSION}.tar.gz ${CARLA_ROOT}/CARLA_${CARLA_VERSION}/Import
cd CARLA_${CARLA_VERSION} && ./ImportAssets.sh && cd ..
mv ${CARLA_ROOT}/CARLA_${CARLA_VERSION}/Import/AdditionalMaps_${CARLA_VERSION}.tar.gz .
