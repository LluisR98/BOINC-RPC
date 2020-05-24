#
# Same commands as the manual method but in script.
#
sudo add-apt-repository universe
sudo apt update
sudo apt install python2 -y
sudo curl https://bootstrap.pypa.io/get-pip.py --output get-pip.py
sudo python2 get-pip.py
sudo pip install tabulate
sudo rm get-pip.py
