from pyspark.sql import SparkSession

import app.ml as ml
from flask import Flask
global spark


def create_app():
    app = Flask(__name__)
    spark = SparkSession.builder.master("local[2]").appName("ml").config("spark.executor.memory", "1g").config("spark.jars", "postgresql-42.2.19.jar") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("INFO")
    ml.init_app(app, spark)
    return app
