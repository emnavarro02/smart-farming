FROM ubuntu AS coordinator
# Installing prerequisites
RUN apt-get update && apt-get upgrade -y
RUN apt-get install mosquitto python3 python3-pip -y
RUN pip3 install requests paho-mqtt cryptography pyrebase
RUN pip3 install --upgrade google-auth-oauthlib
#  Adding configuration files
ADD default.conf /etc/mosquitto/conf.d/
ADD password_file /etc/mosquitto/
# adding application files
ADD client/* /srv/grootfarm/coordinator/client/
# Default mosquitto port
EXPOSE 1883/tcp
CMD ["mosquitto","-c", "/etc/mosquitto/mosquitto.conf"]