# Import spark
import logging
from typing import List

from flask_sqlalchemy import SQLAlchemy
from pyspark.sql import SparkSession

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Recommendation:
    service: str
    rate: float

    # parameterized constructor
    def __init__(self, service, rate):
        self.service = service
        self.rate = rate

    def serialize(self):
        return {
            'service': self.service,
            'rate': self.rate
        }


class RecommendationService:
    """A recommendation engine"""

    spark: SparkSession
    db: SQLAlchemy

    def __init__(self, sc, db):
        """Init the recommendation engine given a Spark context and a dataset path
        """

        logger.info("Starting up the Recommendation Engine: ")
        self.spark = sc
        self.db = db

    def recommend(self, user_id: int) -> List[Recommendation]:
        self.spark.sparkContext.parallelize([user_id, user_id, user_id, user_id, user_id]).collect()
        result = [Recommendation(service="", rate=0.001), Recommendation(service="", rate=0.001),
                  Recommendation(service="", rate=0.001)]
        return result
