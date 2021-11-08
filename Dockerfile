FROM python:3

RUN apt-get update && apt-get -y install libpq-dev

# Download wait-for-it.sh
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /
RUN chmod +x /wait-for-it.sh

# Install pip modules
WORKDIR /app
ADD ./requirements.txt /app/
RUN pip install -r requirements.txt

# Add django source code
ADD ./save_the_computer /app/save_the_computer/
ADD ./products /app/products/
ADD ./manage.py /app/

# Add entrypoints (django, celery-worker, celery-beat)
ADD ./entrypoints /entrypoints
RUN chmod +x /entrypoints/*.sh

ENV PYTHONUNBUFFERED=0

CMD echo ERROR: you should set entrypoint in your docker-compose.yml!