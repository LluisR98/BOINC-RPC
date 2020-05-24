# Data collector for BOINC via RPC.

## Differences between boinc.py and boinc-min.py
The code ```boinc.py``` is the corrected version of the original author, the ```--output``` parameter allows to create a .txt file ready to be imported in Prometheus. The code ```boinc-min.py``` is the corrected version of the original author and minimized of the original code, it does not allow to create a .txt file ready to be imported in Prometheus.

The code is written in ```Python 2```, the commands are fully functional. In case of returning error in the execution of the code run with ```python2``` and install the dependencies manually. The code has been executed and tested on the ```Ubuntu``` distribution in ```20.04 LTS``` on ```AMD64``` version and ```Raspberry Pi 4 pre-configured image```. In other distributions could be functional without having to modify the code, the installation of packages can be different depending on the distribution and the version

> **Possible issue**: The collector does not always get the 100% of the task data, in ```boinc.py``` as in ```boinc-min.py``` it happens.

## How to install Python 2 and PIP on Ubuntu 20.04 LTS [Method 1, manual mode]:
```
sudo add-apt-repository universe
sudo apt update
sudo apt install python2 -y
curl https://bootstrap.pypa.io/get-pip.py --output get-pip.py
sudo python2 get-pip.py
sudo pip install tabulate
```

## How to install Python 2 and PIP on Ubuntu 20.04 LTS [Method 2, automated mode]:
```
cd ./GUIRPC-Py2
chmod +x ./setup.sh
./setup.sh
```

## How to run ```boinc.py``` to get BOINC statistics:
```
python boinc.py --nodes "[IPs]" --password "[PASS]"
```

- [IPs]: Comma-separated IPs, e.g. ```--nodes "192.168.1.10,192.168.1.11,192.168.1.13"```. They have to be accessible, be careful with services denying requests (like iptables).
- [PASS]: Communication password (same password that was used to create the Docker containers), ```--password "qwerty"```. Please do not use ```qwerty``` or similar as a password, use a more secure password... ;)
- Extra:
    -   ```--port "9999"```: You can specify a communication port, by default ```31416```.
    -   ```--output "archivo.txt"```: You can specify if you want it to be saved.

## How to run ```boinc-min.py``` to get BOINC statistics:
```
python boinc-min.py --nodes "[IPs]" --password "[PASS]"
```

- [IPs]: Comma-separated IPs, e.g. ```--nodes "192.168.1.10,192.168.1.11,192.168.1.13"```.
- [PASS]: Communication password (same password that was used to create the Docker containers), ```--password "qwerty"```. Please do not use ```qwerty``` or similar as a password, use a more secure password... ;)

![Made with Python](https://raw.githubusercontent.com/BraveUX/for-the-badge/dev/src/images/badges/made-with-python.svg)
