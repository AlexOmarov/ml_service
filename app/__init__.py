from flask_sqlalchemy import SQLAlchemy
from pyspark.sql import SparkSession

import app.modules as modules
from flask import Flask

app = Flask(__name__)
app.config.from_object('config.Config')

spark = SparkSession.builder \
    .master("local[2]") \
    .appName("ml") \
    .config("spark.executor.memory", "1g") \
    .config("spark.jars", "clickhouse-jdbc-0.3.1.jar") \
    .getOrCreate()
spark.sparkContext.setLogLevel("INFO")

db = SQLAlchemy(app)


def init():
    modules.init()
    return app
