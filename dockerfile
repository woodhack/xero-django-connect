# syntax=docker/dockerfile:1
FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /xero
COPY requirements.txt /xero/
RUN pip install -r requirements.txt

# Set timezone
RUN apt-get update && apt-get install -y tzdata
ENV TZ=UTC

COPY . /xero/