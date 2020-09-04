# antimicro-nonX
Emulate some of Antimicro's functionality for console programs, without X support

# Installation
```
sudo apt-get install python3-yaml
git clone https://github.com/mad-ady/antimicro-nonX.git
sudo cp antimicro-nonX/antimicro-nonX.py /usr/local/bin
sudo cp antimicro-nonX/example.yaml /etc/antimicro-nonX.yaml
sudo cp antimicro-nonX/antimicro-nonX.service /etc/systemd/system/
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
sudo service antimicro-nonX start
sudo systemctl enable antimicro-nonX
```
Troubleshooting:
```
sudo journalctl -f -u antimicro-nonX
```