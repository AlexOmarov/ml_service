FROM python:3.7-alpine

WORKDIR ml_service

RUN apk --update add bash nano
ENV STATIC_URL /static
ENV STATIC_PATH /static
COPY . .
EXPOSE 5000
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python","src/com/dungeonswdragons/ml_service/app.py"]