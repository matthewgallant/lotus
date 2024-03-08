# syntax=docker/dockerfile:1

FROM python:3.11-slim-buster

WORKDIR /lotus

ENV LOTUS_ENVIRONMENT prod

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ENTRYPOINT ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app()"]
