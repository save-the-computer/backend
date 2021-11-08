#!/bin/bash

/wait-for-it.sh -t 0 $MARIADB_HOST:$MARIADB_PORT
/wait-for-it.sh -t 0 $RABBITMQ_HOST:$RABBITMQ_PORT

# important! last line should be exec, so the process can receive SIGTERM from docker stop.
exec celery -A products beat --loglevel=info