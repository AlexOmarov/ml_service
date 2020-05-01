FROM python:3.7-alpine

WORKDIR ml_service

RUN apk --update add bash nano
ENV STATIC_URL /static
ENV STATIC_PATH /var/ml_service/app/static
COPY . /var/ml_service/app
COPY ./requirements.txt /var/ml_service/venv/requirements.txt
EXPOSE 5000
RUN pip install --no-cache-dir -r /var/ml_service/venv/requirements.txt
CMD ["python","/var/ml_service/app/src/com/dungeonswdragons/ml_service/app.py"]