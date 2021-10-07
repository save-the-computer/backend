FROM python:3

RUN apt-get update && apt-get -y install libpq-dev

ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /
RUN chmod +x /wait-for-it.sh

WORKDIR /app
ADD ./requirements.txt /app/
RUN pip install -r requirements.txt

ADD ./save_the_computer /app/save_the_computer/
ADD ./products /app/products/
ADD ./manage.py /app/

ENV PYTHONUNBUFFERED=0

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
