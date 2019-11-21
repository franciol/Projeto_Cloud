#!/bin/bash
sudo apt update;
sudo snap install couchdb;
sudo cp /Projeto_Cloud /var/snap/couchdb/current/etc -f;