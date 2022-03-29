### Machine learning microservice 
Microservice which is responsible for machine learning processing.  
Is included in a backend system architecture.
Uses Flask, Spark, Clickhouse as a data storage
Service chooses elements for recommendation based on previous user activity. Uses markov chain algorithm as a base

Clickhouse instance is required for service to launch.
First, configure venv interp. Download all requirements, then launch `app.py` with envs:
```properties
PYTHONUNBUFFERED=1;DATABASE_URL=jdbc:clickhouse://ml_service:ml_service@localhost:8123/ml_service?currentSchema=ml_service;SPARK_PARTITIONS=4;DATABASE_DRIVER=ru.yandex.clickhouse.ClickHouseDriver
```
Use dockerfile to launch service. Bind ports - `5000:5000`.

Web endpoint `recommend` is exposed   
Needed env variables:
```properties
DATABASE_URL=jdbc:clickhouse://ml_service:ml_service@localhost:8123/ml_service?currentSchema=ml_service; DATABASE_DRIVER=ru.yandex.clickhouse.ClickHouseDriver; SPARK_PARTITIONS=4
```