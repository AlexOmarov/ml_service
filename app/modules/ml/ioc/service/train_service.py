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


def vectors(iterator, services) -> List[ClientVector]:
    result: list = []
    row = next(iterator, "exhausted")

    # Проверяем каждую услугу на вхождение в услуги клиента и строим результат -
    # [client1: [service1: 1, service2: 0], client2: [service1: 0, service2: 1]]
    while row != "exhausted":
        vector = {}
        for service in services:
            client_services = row[1].replace('\'', '').replace('[', '').replace(']', '').split(',')
            vector[service[0]] = 1 if client_services.__contains__(service[0]) else 0
        result.append(ClientVector(row[0], vector))
        row = next(iterator, "exhausted")
    # TODO: Делать матрицу здесь, потом мерджить ее с остальными партициями
    return iter(result)


def get_conjugation(client_vectors):
    result = {}
    # O(n^2), можно оптимизировать - заполнять только половину матрицы и реверсировать ее
    # В итоге должна получиться матрица всех клиентов со всеми
    for client_vector in client_vectors:
        vector = {}

        for other_client_vector in client_vectors:
            vector[other_client_vector.id] = calculate_euclidian(client_vector.vector, other_client_vector.vector)
        vector = sorted(vector.items(), key=lambda item: item[0])
        result[client_vector.id] = vector
    return result


class TrainService:
    spark: SparkSession

    def __init__(self, sc):
        self.spark = sc

    def train(self):
        # [client1: [service1: 1, service2: 0], client2: [service1: 0, service2: 1]]
        client_vectors: List = self.getData()
        conjugation_matrix = get_conjugation(client_vectors)
        if len(conjugation_matrix) < 1:
            print("df is empty")
        else:
            print(conjugation_matrix)
            db = DBSCAN(eps=epsilon, min_samples=min_samples, metric="precomputed").fit(conjugation_matrix)
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
                    "(SELECT toString(client) as client, toString(groupUniqArray(service)) as services from history GROUP BY client)"
                    ") foo") \
            .option("driver", Config.DATABASE_DRIVER) \
            .option("numPartitions", Config.SPARK_PARTITIONS) \
            .option("lowerBound", 0) \
            .option("upperBound", upper) \
            .option("partitionColumn", "num") \
            .load().rdd.mapPartitions(lambda iterator: vectors(iterator, services)).collect()
