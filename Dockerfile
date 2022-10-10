# syntax=docker/dockerfile:1

FROM python:3.10-slim-buster

RUN apt-get update && apt-get install -y \
    libmagic-dev \
		&& rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .
RUN pip3 install .

CMD ["bd-bagarre"]
