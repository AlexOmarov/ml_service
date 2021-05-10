# Import spark
import logging
from typing import List

from flask_sqlalchemy import SQLAlchemy
from pyspark.sql import SparkSession

from modules.ml.dto.recommendation import Recommendation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
