#!/bin/bash

/wait-for-it.sh -t 0 $MARIADB_HOST:$MARIADB_PORT
/wait-for-it.sh -t 0 $INFLUXDB_HOST:$INFLUXDB_PORT

if [ -z "$DJANGO_PORT" ]; then
    export DJANGO_PORT=8000
fi

if [ -z "$DJANGO_BIND_ADDRESS" ]; then
    export DJANGO_BIND_ADDRESS=0.0.0.0
fi

python manage.py migrate

# important! last line should be exec, so the process can receive SIGTERM from docker stop.
exec python manage.py runserver $DJANGO_BIND_ADDRESS:$DJANGO_PORT