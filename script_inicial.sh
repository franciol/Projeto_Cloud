#!/bin/bash
sudo apt update;
sudo apt install awscli -y;
aws configure;
sudo apt install python3-pip -y;
pip3 install flask paramiko boto3;
python3 script.py;
