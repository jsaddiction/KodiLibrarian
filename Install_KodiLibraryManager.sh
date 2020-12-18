#!/bin/bash

#### USER SETTINGS ###
# Install directory: can not be a root directory
installDirectory="/scripts/KodiLibraryManager"

### Scripts variables
parentDir="$(dirname ${installDirectory})"
requirementsFile="${installDirectory}/requirements.txt"

apt update

echo "********** INSTALLING GIT **********"
apt install git -y

echo "********** INSTALLING PYTHON3 **********"
apt install python3 -y
apt install python3-pip -y

if [ ! -d ${parentDir} ]
then
    echo "*********** Creating parent script Directory ************"
    error=$(mkdir -p ${parentDir} 2>&1) || { echo "Failed to create directory ${parentDir}. ERROR: ${error}" ; exit 1; }
    error=$(chmod -R ug+rw ${parentDir} 2>&1) || { echo "Failed to set permissions on ${parentDir}. ERROR: ${error}" ; exit 1; }
fi

### Clone KodiLibraryManager or update if already exists ###
if [ ! -d ${installDirectory} ]
then
    echo "********** CLONING KODI_Library_Manager **********"
    error=$(git clone https://github.com/jsaddiction/SharedLibraryManager.git ${installDirectory} 2>&1) || { echo "Failed to clone repo into ${installDirectory}. ERROR: ${error}" ; exit 1; }
else
    echo "********** UPDATING KODI_Library_Manager **********"
    error=$(git -C ${installDirectory} pull 2>&1) || { echo "Failed to update local repo. ERROR: ${error}" ; }
fi

### Set permissions and install dependancies
echo "********** Setting Permissions for KODI_Library_Manager **********"
error=$(chmod -R ug+rwx ${installDirectory} 2>&1) || { echo "Failed to set permissions on ${installDirectory}. ERROR: ${error}" ; exit 1;}

echo "********** INSTALLING DEPENDENCIES **********"
error=$(python3 -m pip install -r ${requirementsFile} 2>&1) || { echo "Failed to install dependencies. ERROR: ${error}" ; exit 1; }
