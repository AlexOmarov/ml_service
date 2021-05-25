import logging
from typing import List
from uuid import UUID

from pyspark.sql import SparkSession

from config import Config
from modules.ml.ioc.entity.recommendation import Recommendation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecommendationService:
    spark: SparkSession

    def __init__(self, sc, db):
        self.spark = sc

    def recommend(self, user_id: UUID) -> List[Recommendation]:
        service_vectors = self.getServiceVectors()
        client_vector = self.getClientVector(user_id)

        return sorted(
            {**self.longTerm(service_vectors, client_vector),
             **self.shortTerm(service_vectors, client_vector, self.getMarkov())}.items(),
            key=lambda item: item.rate
        )[:10]

    def longTerm(self, service_vectors, client_vector) -> dict:
        print("Performing long term recommendation")
        print(client_vector)
        print(service_vectors)
        result = {}
        return result

    def shortTerm(self, service_vectors, client_vector, markov) -> dict:
        print("Performing short term recommendation")
        print(client_vector)
        print(service_vectors)
        print(markov)
        result = {}
        return result

    def getServiceVectors(self):
        return self.spark.read.format("jdbc").option("url", Config.SQLALCHEMY_DATABASE_URI) \
            .option("dbtable",
                    "("
                    "WITH (SELECT max(updateDate) FROM client_vector) AS recent "
                    "SELECT toString(service) as service, toString(clusters) as vector, "
                    "version from service_vector WHERE updateDate = recent) foo") \
            .option("driver", Config.DATABASE_DRIVER).load().collect()

    def getClientVector(self, user_id):
        return self.spark.read.format("jdbc").option("url", Config.SQLALCHEMY_DATABASE_URI) \
            .option("dbtable", "("
                               "WITH (SELECT max(updateDate) FROM client_vector) AS recent "
                               "SELECT toString(client) as client, toString(clusters) as vector, "
                               "version from client_vector WHERE client  = '"
                    + user_id.__str__() + "' AND updateDate = recent) foo") \
            .option("driver", Config.DATABASE_DRIVER).load().collect()

    def getMarkov(self):
        return self.spark.read.format("jdbc").option("url", Config.SQLALCHEMY_DATABASE_URI) \
            .option("dbtable", "("
                               "WITH (SELECT max(updateDate) FROM markov) AS recent "
                               "SELECT toString(cluster) as cluster, toString(value) as vector, version "
                               "from markov WHERE updateDate = recent) foo") \
            .option("driver", Config.DATABASE_DRIVER).load().collect()
