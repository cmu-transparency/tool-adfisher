#!/bin/bash


### Install os dependencies
apt-get update

# Install gui
apt-get install -y ubuntu-desktop gnome-session-flashback

# Required for browsing
apt-get install -y firefox

# Required for headless testing
apt-get install -y xvfb

# Required for data analysis
apt-get install -y python3-numpy python3-scipy python3-matplotlib

# Requiured for python dependencies
apt-get install -y python3-pip python3-dev

# Required for pyre2 dependencies
apt-get install -y git build-essential
cd ~
git clone https://code.googlesource.com/re2
cd re2
make test
sudo make install

### Install python dependencies
sudo pip3 install -r /vagrant/requirements.txt

# Fetch nltk stopwords corpus
python3 -m nltk.downloader -d /usr/share/nltk_data stopwords

# get geckodriver
wget -q https://github.com/mozilla/geckodriver/releases/download/v0.23.0/geckodriver-v0.23.0-linux64.tar.gz
tar -xvzf geckodriver*
chmod +x geckodriver
sudo mv geckodriver* /usr/local/bin
