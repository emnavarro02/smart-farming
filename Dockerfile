FROM ubuntu AS coordinator
# Installing prerequisites
RUN apt-get update && apt-get upgrade -y
RUN apt-get install mosquitto python3 python3-pip -y
RUN pip3 install requests paho-mqtt cryptography pyrebase
RUN pip3 install --upgrade google-auth-oauthlib
#  Adding configuration files
ADD coordinator/mosquitto.conf /etc/mosquitto/conf.d/
ADD coordinator/passwords_file /etc/mosquitto/
# addming application files 
ADD coordinator/client/* /srv/grootfarm/coordinator/client/
# Default mosquitto port
EXPOSE 1883/tcp
CMD ["mosquitto"]
