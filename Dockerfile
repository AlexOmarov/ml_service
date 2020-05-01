FROM python:3.7-alpine

WORKDIR ml_service

RUN apk --update add bash nano
ENV STATIC_URL /static
ENV STATIC_PATH /app/static
COPY . .
EXPOSE 5000
RUN pip install --no-cache-dir -r requirements/prod.txt
ENTRYPOINT [ "waitress-serve","--port=5000", "--call", "app:create_app" ]