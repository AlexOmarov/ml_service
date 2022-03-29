### Machine learning microservice 
Microservice which is responsible for machine learning processing.  
Is included in a backend system architecture.
Uses Flask, Spark, Clickhouse as a data storage
Service chooses elements for recommendation based on previous user activity. Uses markov chain algorithm as a base

Use dockerfile to launch service. Bind ports - `5000:5000`.
Clickhouse instance is required for service to launch.
Web endpoint `recommend` 
Needed env variables:
```properties
DATABASE_URL=jdbc:clickhouse://ml_service:ml_service@localhost:8123/ml_service?currentSchema=ml_service; DATABASE_DRIVER=ru.yandex.clickhouse.ClickHouseDriver; SPARK_PARTITIONS=4
```