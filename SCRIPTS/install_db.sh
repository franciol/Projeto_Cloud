#!/bin/bash
sudo apt update;
sudo snap install couchdb;
sudo cp Projeto_Cloud/SCRIPTS/local.ini /var/snap/couchdb/current/etc -f;
sudo reboot;