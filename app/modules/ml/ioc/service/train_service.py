import logging
import math
from typing import List

from pyspark.sql import SparkSession
from sklearn.cluster import DBSCAN

from config import Config
from modules.ml.ioc.entity.client_vector import ClientVector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

epsilon = 0.09
min_samples = 4


def calculate_euclidian(vector, other_vector):
    return math.sqrt(sum((vector.get(d, 0) - other_vector.get(d, 0)) ** 2 for d in set(vector) | set(other_vector)))


def vectors(iterator) -> List[ClientVector]:
    result: list = []
    row = next(iterator, "exhausted")

    # Проверяем каждую услугу на вхождение в услуги клиента и строим результат -
    # [client1: [service1: 1, service2: 0], client2: [service1: 0, service2: 1]]
    while row != "exhausted":
        vector = {}
    # TODO: Делать матрицу здесь, потом мерджить ее с остальными партициями
    return iter(result)


class TrainService:
    spark: SparkSession

    def __init__(self, sc):
        self.spark = sc

    def train(self):
        # [client1: [service1: 1, service2: 0], client2: [service1: 0, service2: 1]]
        client_vectors: List = self.getData()
        if len(client_vectors) < 1:
            print("df is empty")
        else:
            print(client_vectors)
            db = DBSCAN(eps=epsilon, min_samples=min_samples, metric="precomputed").fit(client_vectors)
            labels = db.labels_
            # TODO: Store trained model
            print(labels.size)
            print(labels)

    def getData(self) -> List:
        # Получаем все услуги
        services = self.spark.read.format("jdbc").option("url", Config.SQLALCHEMY_DATABASE_URI) \
            .option("dbtable", "(select toString(id) as service from ml_service.service) foo") \
            .option("driver", Config.DATABASE_DRIVER) \
            .load().collect()
        upper = self.spark.read.format("jdbc").option("url", Config.SQLALCHEMY_DATABASE_URI) \
            .option("dbtable", "(select count(DISTINCT client) as count from ml_service.history) foo") \
            .option("driver", Config.DATABASE_DRIVER) \
            .load().collect()[0]["count"]

        return self.spark.read.format("jdbc").option("url", Config.SQLALCHEMY_DATABASE_URI) \
            .option("dbtable",
                    "("
                    "select *, rowNumberInAllBlocks() as num FROM "
                    "("
                    "SELECT clients_first.client, clients_second.client,"
                    "sqrt(length(arrayConcat(clients_first.services, clients_second.services)) "
                    "- length(clients_first.services)"
                    "+ length(arrayConcat(clients_first.services, clients_second.services)) "
                    "- length(clients_first.services)) AS euclidian"
                    "FROM"
                    "(SELECT client, groupUniqArray(service) as services, 1 as equalityWorkaround"
                    "FROM (SELECT client, service, max(updateTime) as endTime"
                    "from history"
                    "where updateType = 'END'"
                    "group by client, service) end"
                    "inner join (SELECT client, service, max(updateTime) as startTime"
                    "from history"
                    " where updateType = 'START'"
                    "group by client, service) start"
                    " on end.service = start.service and end.client = start.client"
                    "where startTime >= endTime"
                    " GROUP BY client) clients_first"

                    "inner join"

                    "(SELECT client, groupUniqArray(service) as services, 1 as equalityWorkaround"
                    " FROM (SELECT client, service, max(updateTime) as endTime"
                    "from history"
                    " where updateType = 'END'"
                    " group by client, service) end"
                    " inner join (SELECT client, service, max(updateTime) as startTime"
                    " from history"
                    "where updateType = 'START'"
                    "  group by client, service) start"
                    " on end.service = start.service and end.client = start.client"
                    " where startTime >= endTime"
                    " GROUP BY client) clients_second"

                    "on equals(clients_first.equalityWorkaround, clients_second.equalityWorkaround);"
                    ")"
                    ") foo") \
            .option("driver", Config.DATABASE_DRIVER) \
            .option("numPartitions", Config.SPARK_PARTITIONS) \
            .option("lowerBound", 0) \
            .option("upperBound", upper) \
            .option("partitionColumn", "num") \
            .load().rdd.mapPartitions(lambda iterator: vectors(iterator)).collect()
