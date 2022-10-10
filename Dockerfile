# syntax=docker/dockerfile:1

FROM python:3.10-slim-buster

RUN apt install -y \
    libmagic-dev

WORKDIR /app

COPY . .
RUN pip3 install .

CMD ["bd-bagarre"]
