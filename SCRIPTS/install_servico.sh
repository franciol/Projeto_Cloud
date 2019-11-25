#!/bin/bash
sudo apt install -y;
sudo apt install python3-pip -y;
pip3 install flask;
git clone https://github.com/franciol/APS1_ComputacaoNuvem.git;
nohup python3 APS1_ComputacaoNuvem/server.py &;