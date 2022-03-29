import logging
import math
from typing import List

import numpy as np
from pyspark.sql import SparkSession
from sklearn.cluster import DBSCAN

from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

epsilon = 27.5
min_samples = 3


def calculate_euclidian(vector, other_vector):
    return math.sqrt(sum((vector.get(d, 0) - other_vector.get(d, 0)) ** 2 for d in set(vector) | set(other_vector)))


def vectors(iterator):
    res = {}
    row = next(iterator, "exhausted")

    # Проверяем каждую услугу на вхождение в услуги клиента и строим результат -
    # [[client, satelite, euclidian], [client, satelite, euclidian]]
    print("BEGIN!@!!")
    while row != "exhausted":
        if row[0] in dict.keys(res):
            vector = res[row[0]]
        else:
            vector = {}
        vector[row[1]] = row[2]
        res[row[0]] = vector
        row = next(iterator, "exhausted")
    result = np.array([[res[client][satelite] for satelite in sorted(res[client])] for client in sorted(res)])
    response = [result]
    return iter(response)


class TrainService:
    spark: SparkSession

    def __init__(self, sc):
        self.spark = sc

    def train(self):
        # [client1: [service1: 1, service2: 0], client2: [service1: 0, service2: 1]]
        client_vectors: List = self.getData()
        print("client_vectors")
        print(client_vectors)
        print(client_vectors[0])
        if len(client_vectors) < 1:
            print("df is empty")
        else:
            db = DBSCAN(eps=epsilon, min_samples=min_samples, metric="precomputed").fit(client_vectors[0])
            labels = db.labels_
            # TODO: Store trained model
            print(labels.size)
            print(labels)

    def getData(self) -> List:
        return self.spark.read.format("jdbc").option("url", Config.SQLALCHEMY_DATABASE_URI) \
            .option("dbtable",
                    "("
                    "select  toString(firstServices.id)                     as service, "
                    "toString(secondServices.id)                    as satelite, "
                    "sqrt(length(arrayConcat(firstServices.clients, secondServices.clients)) "
                    "- length(firstServices.clients) "
                    " + length(arrayConcat(firstServices.clients, secondServices.clients)) - "
                    "length(firstServices.clients)) AS euclidian from "
                    "(select id, ids as clients, 1 as equalityWorkaround from "
                    "(SELECT  groupUniqArray(start.client) as ids, start.service as service "
                    "FROM (SELECT client, service, max(updateTime) as endTime "
                    "from history "
                    "where updateType = \'END\' "
                    "group by client, service) end "
                    "right join (SELECT client, service, max(updateTime) as startTime "
                    " from history "
                    " where updateType = \'START\' "
                    " group by client, service) start "
                    "   on end.service = start.service and end.client = start.client "
                    "where startTime >= endTime "
                    "   OR isNull(endTime) == 1 "
                    "GROUP BY service) enabledServices right outer join service on id = service) firstServices "

                    "inner join "

                    "(select id, ids as clients, 1 as equalityWorkaround from "
                    "(SELECT  groupUniqArray(start.client) as ids, start.service as service "
                    "FROM (SELECT client, service, max(updateTime) as endTime "
                    "from history "
                    " where updateType = \'END\' "
                    "group by client, service) end "
                    "right join (SELECT client, service, max(updateTime) as startTime "
                    "from history "
                    " where updateType = \'START\' "
                    " group by client, service) start "
                    "on end.service = start.service and end.client = start.client "
                    "where startTime >= endTime "
                    "   OR isNull(endTime) == 1 "
                    "GROUP BY service) enabledServices right outer join service on id = service) secondServices "
                    "on equals(firstServices.equalityWorkaround, secondServices.equalityWorkaround) "
                    ") foo") \
            .option("driver", Config.DATABASE_DRIVER) \
            .load().rdd.mapPartitions(lambda iterator: vectors(iterator)).collect()
