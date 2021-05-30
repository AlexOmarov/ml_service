import logging
from typing import List
from uuid import UUID

import numpy as np
from pyspark.sql import SparkSession

from config import Config
from modules.ml.ioc.entity.recommendation import Recommendation
from scipy.spatial import distance

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def euclid(v, vector):
    return distance.euclidean(v, vector)


def getMostSuitableServices(service_vectors, vector):
    result = {}
    for k, v in service_vectors:
        result[k] = Recommendation(k, euclid(v, vector))
    return result


class RecommendationService:
    spark: SparkSession

    def __init__(self, sc, db):
        self.spark = sc

    def recommend(self, user_id: UUID) -> List[Recommendation]:
        service_vectors = self.getServiceVectors()
        client_vector = self.getClientVector(user_id)
        last_service_vector = self.getLastServiceVector(user_id)
        long = self.longTerm(service_vectors, client_vector)
        long.update(self.shortTerm(service_vectors, self.getMarkov(), last_service_vector))
        return sorted(long.items(), key=lambda item: item.rate)[:10]

    def longTerm(self, service_vectors, client_vector) -> dict:
        print("Performing long term recommendation")
        print(client_vector)
        print(service_vectors)
        return getMostSuitableServices(service_vectors, client_vector)

    def shortTerm(self, service_vectors, markov, last_service_vector) -> dict:
        print("Performing short term recommendation")
        return getMostSuitableServices(service_vectors, np.dot(last_service_vector, markov))

    def getServiceVectors(self):
        result = {}
        rows = self.spark.read.format("jdbc").option("url", Config.SQLALCHEMY_DATABASE_URI) \
            .option("dbtable",
                    "("
                    "select toString(service) as service, toString(mapValues(clusters)) as vector from service_vector ORDER BY updateDate DESC LIMIT 1 by service"
                    ") foo") \
            .option("driver", Config.DATABASE_DRIVER).load().collect()
        for k in rows:
            result[k[0]] = k[1].replace("[", "").replace("]", "").split(",")
        return result

    def getClientVector(self, user_id):
        rows = self.spark.read.format("jdbc").option("url", Config.SQLALCHEMY_DATABASE_URI) \
            .option("dbtable", "("
                               "select toString(mapValues(clusters)) as vector from client_vector WHERE client = \'" + user_id.__str__() + "\' ORDER BY updateDate DESC LIMIT 1 by client"
                                                                                                                                           ") foo") \
            .option("driver", Config.DATABASE_DRIVER).load().collect()
        return rows[0][0].replace("[", "").replace("]", "").split(",")

    def getMarkov(self):
        result = {}
        rows = self.spark.read.format("jdbc").option("url", Config.SQLALCHEMY_DATABASE_URI) \
            .option("dbtable", "("
                               "select toString(cluster) as cluster, toString(mapValues(value)) as vector from markov ORDER BY updateDate DESC LIMIT 1 by cluster"
                               ") foo") \
            .option("driver", Config.DATABASE_DRIVER).load().collect()
        for k in rows:
            result[k[0]] = k[1].replace("[", "").replace("]", "").split(",")
        return result

    def getLastServiceVector(self, user_id):
        rows = self.spark.read.format("jdbc").option("url", Config.SQLALCHEMY_DATABASE_URI) \
            .option("dbtable",
                    "("
                    "select toString(clusters) from history"
                    " inner join"
                    "service_vector on service_vector.service = history.service WHERE updateType = 'START' and client = \'" + user_id.__str__() + "\' ORDER BY updateTime DESC LIMIT 1"
                                                                                                                                                  ") foo") \
            .option("driver", Config.DATABASE_DRIVER).load().collect()
        return rows[0][0].replace("[", "").replace("]", "").split(",")
