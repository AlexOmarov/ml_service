from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pyspark.sql import SparkSession

import app.modules as modules


app = Flask(__name__)
app.config.from_object('config.Config')


db = SQLAlchemy(app)


def get_app():
    spark = SparkSession.builder \
        .master("local[2]") \
        .appName("ml") \
        .config("spark.executor.memory", "1g") \
        .config("spark.jars", "clickhouse-jdbc-0.3.1.jar") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("INFO")
    modules.init(app, spark, db)
    return app
