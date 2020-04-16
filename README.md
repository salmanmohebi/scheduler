# scheduler
A very simple discrete-event simulator (DES) for channel allocation in 802.11ad based on Simpy.

We are providing an environment for the OpenAI Gym frame work.
Later on we are going to write some Agents to interact with this environment. 

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