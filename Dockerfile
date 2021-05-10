FROM python:3.7-alpine

COPY ./test /test
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR /test
CMD ["python3", "main-tracking.py"] 
