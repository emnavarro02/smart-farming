# smart-farming
Smart Farming project using Raspberry PI and NodeMCU (ESP8266)

```
docker build . -t coordinator:v1
docker run -d -p 1883:1883/tcp coordinator:v1
```

**Windows Only**:
- Refer to https://stackoverflow.com/questions/32800336/pycrypto-on-python-3-5 to see how to install PyCripto on Windows
