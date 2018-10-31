#!/bin/bash

### Install os dependencies
apt-get -y update
apt-get -y upgrade
### Install gui or alternatively, without gui, install xvfp for headless testing
if [ "$1" = "headless" ]; then
    apt-get install -y xvfb
else
    apt-get install -y lightdm unity
    apt-get install -y --no-install-recommends ubuntu-desktop
fi

# Required for browsing
apt-get install -y firefox

# Required for pyre2 dependencies
apt-get install -y libre2-dev

# get geckodriver
wget -q https://github.com/mozilla/geckodriver/releases/download/v0.23.0/geckodriver-v0.23.0-linux64.tar.gz
tar -xvzf geckodriver*
chmod +x geckodriver
mv geckodriver* /usr/local/bin

PYTHON=python3
PIP=pip3
if [ "$2" = "python2" ]; then
    PYTHON=python
    PIP=pip
fi

# Required for data analysis
apt-get install -y $PYTHON-numpy $PYTHON-scipy $PYTHON-matplotlib

# Requiured for python dependencies
apt-get install -y $PYTHON-pip $PYTHON-dev

### Install python dependencies
# $PIP install --upgrade pip
$PIP install -r /vagrant/requirements.txt
$PIP install --upgrade urllib3
$PIP install --upgrade psutil
$PIP install --upgrade sklearn

if [ "$1" == "headless" ]; then
    $PIP install xvfbwrapper
fi

# Fetch nltk stopwords corpus
$PYTHON -m nltk.downloader -d /usr/share/nltk_data stopwords

apt-get -y upgrade
