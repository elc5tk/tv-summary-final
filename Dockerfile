FROM python:3.7-alpine

COPY app/main.py /app/
COPY app/last_seen_id.txt /app/
COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

WORKDIR /app
