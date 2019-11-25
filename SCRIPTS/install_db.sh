#!/bin/bash
sudo apt update;
sudo snap install couchdb -y;
sudo cp Projeto_Cloud/local.ini /var/snap/couchdb/current/etc -f;
sudo reboot;