# scheduler
This a simple discrete-event simulator (DES) for the channel allocation in 802.11ad based on OpenAI Gym and Simpy.

Setup Python environment
```
$ sudo apt-get install python3-pip python3-dev
$ sudo pip3 install virtualenvwrapper
$ echo "export VIRTUALENVWRAPPER_PYTHON=$(which python3.7)" >> ~/.bashrc
$ echo "alias v.activate=\"source $(which virtualenvwrapper.sh)\"" >> ~/.bashrc
$ source ~/.bashrc
$ v.activate
$ mkvirtualenv —python=$(which python3.7) —no-site-packages scheduler
```