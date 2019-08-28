#!/usr/bin/env bash


MANTIS_PATH=/Users/scott/Desktop/Projects/Branches/mantis

# cmake version >=13.
#CMAKE=/home/scott/Downloads/clion-2018.3.3/bin/cmake/linux/bin/cmake
CMAKE=cmake3

pwd=$(cd `dirname $0`;pwd)
DIST_DIR=$pwd/../dist

#DIST_DIR=/opt

rm -rf $DIST_DIR/*

SMARTHOME_DIR=$DIST_DIR/smarthome
mkdir -p $SMARTHOME_DIR

cp -r ../AppServer $SMARTHOME_DIR ; rm -rf ../AppServer/data ; rm -rf ../AppServer/logs ; rm -rf ../AppServer/run
cp -r ../BoxServer $SMARTHOME_DIR ; rm -rf ../BoxServer/data ; rm -rf ../BoxServer/logs ; rm -rf ../BoxServer/run
cp -r ../GreenIotGateServer $SMARTHOME_DIR ; rm -rf ../GreenIotGateServer/data ; rm -rf ../GreenIotGateServer/logs ; rm -rf ../GreenIotGateServer/run
cp -r ../LoginServer $SMARTHOME_DIR ; rm -rf ../LoginServer/data ; rm -rf ../LoginServer/logs ; rm -rf ../LoginServer/run
cp -r ../RealPushServer $SMARTHOME_DIR ; rm -rf ../RealPushServer/data ; rm -rf ../RealPushServer/logs ; rm -rf ../RealPushServer/run


# --- mantis ---
PYTHONPATH=$SMARTHOME_DIR/pythonpath
mkdir -p $PYTHONPATH/mantis/fanbei
cp -r $MANTIS_PATH/fundamental $PYTHONPATH/mantis
cp -r $MANTIS_PATH/sg $PYTHONPATH/mantis
cp -r $MANTIS_PATH/fanbei/smarthome $PYTHONPATH/mantis/fanbei

echo "export PYTHONPATH=`pwd`/pythonpath" > $SMARTHOME_DIR/export_env.sh

