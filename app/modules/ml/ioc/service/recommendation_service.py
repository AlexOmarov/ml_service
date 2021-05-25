import logging
from typing import List, Dict
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


def longTerm(service_vectors, client_vector) -> Dict[Recommendation]:
    print("Performing long term recommendation")
    print(client_vector)
    print(service_vectors)
    result = {}
    return result


def shortTerm(service_vectors, client_vector, markov) -> Dict[Recommendation]:
    print("Performing short term recommendation")
    print(client_vector)
    print(service_vectors)
    print(markov)
    result = {}
    return result


class RecommendationService:
    spark: SparkSession
    db: SQLAlchemy

    def __init__(self, sc, db):
        self.spark = sc
        self.db = db

    def recommend(self, user_id: UUID) -> List[Recommendation]:

        service_vectors = self.spark.read.format("jdbc").option("url", Config.SQLALCHEMY_DATABASE_URI) \
            .option("dbtable",
                    "("
                    "WITH (SELECT max(version) FROM service_vector) AS max_version"
                    "SELECT toString(service) as service, toString(clusters) as vector, version from service_vector WHERE version = max_version"
                    ") foo") \
            .option("driver", Config.DATABASE_DRIVER).load().collect()

        client_vector = self.spark.read.format("jdbc").option("url", Config.SQLALCHEMY_DATABASE_URI) \
            .option("dbtable", "("
                               "WITH (SELECT max(version) FROM client_vector) AS max_version"
                               "(SELECT toString(client) as client, toString(clusters) as vector, version from client_vector WHERE client  = '"
                    + user_id.__str__() + " AND version = max_version) foo").option("driver",
                                                                                    Config.DATABASE_DRIVER).load().collect()

        markov = self.spark.read.format("jdbc").option("url", Config.SQLALCHEMY_DATABASE_URI) \
            .option("dbtable", "("
                               "WITH (SELECT max(version) FROM markov) AS max_version"
                               "(SELECT toString(cluster) as cluster, toString(value) as vector, version from client_vector WHERE client  = '"
                    + user_id.__str__() + " AND version = max_version) foo").option("driver",
                                                                                    Config.DATABASE_DRIVER).load().collect()

        return sorted(
            {**longTerm(service_vectors, client_vector), **shortTerm(service_vectors, client_vector, markov)}.items(),
            key=lambda item: item.rate
        )[:10]
