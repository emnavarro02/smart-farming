FROM python:alpine AS coordinator
RUN apk update && apk upgrade
RUN apk add mosquitto mosquitto-clients
ADD default.conf /etc/mosquitto/conf.d/
ADD password_file /etc/mosquitto/
# adding application files
ADD client/* /srv/grootfarm/coordinator/client/
# Default mosquitto port
EXPOSE 1883/tcp
# CMD ["python", "app.py"]
CMD ["mosquitto", "-v"] 
#, "-c", "/etc/mosquitto/mosquitto.conf"]