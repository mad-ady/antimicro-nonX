# antimicro-nonX
Emulate some of Antimicro's functionality for console programs, without X support

![Demo](https://img.youtube.com/vi/wxVN7NHgjcU/0.jpg)]

(https://www.youtube.com/watch?v=wxVN7NHgjcU)

# Installation
The system you're installing to needs to have UINPUT support in the kernel.
```
sudo apt-get install python3-yaml python3-pip git evtest
sudo pip3 install evdev==1.1.2
git clone https://github.com/mad-ady/antimicro-nonX.git
sudo cp antimicro-nonX/antimicro-nonX.py /usr/local/bin
sudo chmod a+x /usr/local/bin/antimicro-nonX.py
sudo cp antimicro-nonX/antimicro-nonX-goa-ncmpc.yaml /etc/antimicro-nonX.yaml
sudo cp antimicro-nonX/antimicro-nonX-ncmpc.service /etc/systemd/system/
sudo vi /etc/antimicro-nonX.yaml
```

# Configuration file
See the attached config files for example config.


# Usage
Either start manually:
```
sudo /usr/local/bin/antimicro-nonX.py /etc/antimicro-nonX.yaml
```
Or via systemd:
```
sudo service antimicro-nonX-ncmpc start
sudo systemctl enable antimicro-nonX-ncmpc
```
Troubleshooting:
```
sudo journalctl -f -u antimicro-nonX-ncmpc
```
Note - there is a problem with more recent evdev python packages that is not yet resolved: https://github.com/gvalkov/python-evdev/issues/134
