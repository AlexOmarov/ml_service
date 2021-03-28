from pyspark.sql import SparkSession

import app.ml as ml
from flask import Flask
global spark


def create_app():
    app = Flask(__name__)
    spark = SparkSession.builder.master("local[2]").appName("ml").config("spark.executor.memory", "1g") \
        .getOrCreate().sparkContext
    spark.setLogLevel("INFO")
    ml.init_app(app, spark)
    return app
