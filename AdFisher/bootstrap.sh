#!/bin/bash

### Install os dependencies
apt-get update
apt-get upgrade
apt-get dist-upgrade

### Install gui
apt-get install -y lightdm unity
apt-get install -y --no-install-recommends ubuntu-desktop
#apt-get install -y ubuntu-desktop

# Alternatively, without gui, install xvfp for headless testing
#apt-get install xvfb

# Required for browsing
apt-get install -y firefox

# Required for data analysis
apt-get install -y python3-numpy python3-scipy python3-matplotlib

# Requiured for python dependencies
apt-get install -y python3-pip python3-dev

# Required for pyre2 dependencies
apt-get install -y libre2-dev
# apt-get install -y libre2-1v5
# apt-get install -y git build-essential
# cd ~
# git clone https://code.googlesource.com/re2
# cd re2
# make test
# sudo make install

### Install python dependencies
# pip3 install --upgrade pip
pip3 install -r /vagrant/requirements.txt
pip3 install --upgrade urllib3
pip3 install --upgrade psutil

# Fetch nltk stopwords corpus
python3 -m nltk.downloader -d /usr/share/nltk_data stopwords

# get geckodriver
wget -q https://github.com/mozilla/geckodriver/releases/download/v0.23.0/geckodriver-v0.23.0-linux64.tar.gz
tar -xvzf geckodriver*
chmod +x geckodriver
mv geckodriver* /usr/local/bin
