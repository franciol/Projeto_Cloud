#!/bin/bash
sudo apt update;
sudo apt-get install -y apt-transport-https gnupg ca-certificates;
echo "deb https://apache.bintray.com/couchdb-deb bionic main" | sudo tee -a /etc/apt/sources.list.d/couchdb.list;
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 8756C4F765C9AC3CB6B85D62379CE192D401AB61;
sudo apt update;
sudo apt install -y couchdb;