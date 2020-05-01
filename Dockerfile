FROM python:3.7-alpine

WORKDIR ml_service

RUN apk --update add bash nano
ENV STATIC_URL /static
ENV STATIC_PATH /var/ml_service/app/static
COPY ./requirements.txt /var/ml_service/requirements.txt
RUN pip install --no-cache-dir -r /var/ml_service/requirements.txt
CMD [ "python", "./your-daemon-or-script.py" ]