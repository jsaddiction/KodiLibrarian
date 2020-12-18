#!/bin/bash

apt update

echo "********** INSTALLING GIT **********"
apt install git -y

echo "********** INSTALLING PYTHON3 **********"
apt install python3 -y
apt install python3-pip -y

### Clone KodiCoupler or update if already exists ###
if [ ! -d "/config/scripts/KodiLibraryManager" ] 
then
    echo "********** CLONING KODI_Library_Manager **********"
    git clone https://github.com/jsaddiction/KodiLibraryManager.git /config/scripts/KodiCoupler
else
    echo "********** UPDATING KODI_Library_Manager **********"
    git -C /config/scripts/KodiLibraryManager pull
fi

### Set permissions and install dependancies
echo "********** Setting Permissions for KODI_Library_Manager **********"
chmod -R ug+rwx /config/scripts/KodiLibraryManager

echo "********** INSTALLING DEPENDANCIES **********"
python3 -m pip install -r /config/scripts/KodiLibraryManager/requirements.txt