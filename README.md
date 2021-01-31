# smart-farming
Smart Farming project using Raspberry PI and NodeMCU (ESP8266)

docker build . -t coordinator:v1
docker run -d -p 1883:1883/tcp coordinator:v1


### Windows Only:
- Refer to https://stackoverflow.com/questions/32800336/pycrypto-on-python-3-5 to see how to install PyCripto on Windows.


### Change Log

- 1.0.0 (21/11/20201)
  - Now using docker to build the image of the coordinator node
  - Moved from `pyrebase` to `pyrebase4` due to compatibility with Windows.
  - Changed file structure: 
    - "coordinator\client" directory contains coordinator node files. 
    - "sensor-nodes" directory contains sensor nodes and actutators files.   