import logging
from typing import List
from uuid import UUID

from flask_sqlalchemy import SQLAlchemy
from pyspark.sql import SparkSession

from config import Config

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

    def recommend(self, user_id: UUID) -> List[Recommendation]:
        self.spark.sparkContext.parallelize([user_id, user_id, user_id, user_id, user_id]).collect()

        result = self.spark.read.format("jdbc").option("url", Config.SQLALCHEMY_DATABASE_URI) \
            .option("dbtable",
                    "("
                    "select *, rowNumberInAllBlocks() as num FROM "
                    "(SELECT toString(id) as id, toString(service) as service from history WHERE client  = '" + user_id.__str__() + "')"
                                                                                                                          ") foo") \
            .option("driver", Config.DATABASE_DRIVER).load().collect()
        res = []
        for row in result:
            res.append(Recommendation(service=row[1], rate=0.001))
        return res
