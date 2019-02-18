FROM python:3.7.2-alpine3.7

RUN apk add --update bash && rm -rf /var/cache/apk/*

WORKDIR /app

COPY wait-for-it.sh /app

COPY requirements.txt /app

RUN pip install -r requirements.txt

COPY . /app
