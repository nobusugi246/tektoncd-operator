FROM python:3.8-slim

COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt

COPY operator.py /src
CMD kopf run /src/operator.py
