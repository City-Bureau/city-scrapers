FROM python:3.6

COPY requirements.txt /usr/src/app/
RUN pip install -r /usr/src/app/requirements.txt
RUN pip install redis==2.10.6
COPY . /usr/src/app/

ENV PYTHONPATH=/usr/src/app

WORKDIR /usr/src/app
