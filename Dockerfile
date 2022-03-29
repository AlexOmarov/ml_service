FROM tensorflow/tensorflow:latest

WORKDIR ml_service

ENV STATIC_URL /static
ENV STATIC_PATH /app/static
COPY . .

EXPOSE 5000
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN apt-get update
RUN apt-get install -y default-jre
RUN pip install --upgrade -r requirements/prod.txt
ENTRYPOINT [ "waitress-serve","--port=5000", "--call", "app:get_app" ]