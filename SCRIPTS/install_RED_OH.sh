sudo apt update;
sudo apt install python3-pip -y;
pip3 install flask requests;
sudo apt install tmux;
sudo tmux new -d -s execution 'sudo python3 ../server_red_OH.py';

