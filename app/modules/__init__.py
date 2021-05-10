import app.modules.ml as ml

from app import db
from app import spark
from app import app


def init():
    ml.init(app, spark, db)
