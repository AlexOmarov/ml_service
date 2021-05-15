import logging
from typing import List

from flask_sqlalchemy import SQLAlchemy
from pyspark.sql import SparkSession

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Recommendation:
    service: str
    rate: float

    def __init__(self, service, rate):
        self.service = service
        self.rate = rate

    def serialize(self):
        return {
            'service': self.service,
            'rate': self.rate
        }


class RecommendationService:
    spark: SparkSession
    db: SQLAlchemy

    def __init__(self, sc, db):
        self.spark = sc
        self.db = db

    def recommend(self, user_id: int) -> List[Recommendation]:
        self.spark.sparkContext.parallelize([user_id, user_id, user_id, user_id, user_id]).collect()
        # TODO: Make recommendation based on db stored model


        result = [Recommendation(service="", rate=0.001), Recommendation(service="", rate=0.001),
                  Recommendation(service="", rate=0.001)]
        return result
