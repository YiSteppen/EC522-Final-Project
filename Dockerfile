FROM alpine:latest

RUN apk add --no-cache python3 py3-pip gcc python3-dev musl-dev linux-headers

COPY requirements.txt /requirements.txt

RUN pip install --break-system-packages -r /requirements.txt

COPY Source /Source
