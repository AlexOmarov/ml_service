import logging
from typing import Dict, Iterator, List

from pyspark.rdd import RDD
from pyspark.sql import SparkSession
from sklearn.cluster import DBSCAN

from app.commons.db.database_connector import DatabaseConnector
from app.commons.singleton.singleton_meta import SingletonMeta
from pandas import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def calculateSimilarity(history):
    result = []
    for service in history:
        print(service)
        print(history[service])
        row = {}
        x = history[service]["connected"]
        not_x = history[service]["unconnected"]
        for sim in history[service]["sims"]:
            xy = history[service]["sims"][sim]
            # Возьмем всех клиентов, у которых подключен Y и вычтем из них тех, у которых подключен еще и X
            not_xy = history[sim]["connected"] - xy
            distance = 0
            if x != 0:
                distance = xy / x
            row[sim] = distance

        #result.append(Similarity(service, row))
    return result


def matrix(iterator):
    result = {}
    row = next(iterator, "exhausted")
    # работает как индекс для итератора. Нужен для того, чтобы при добавлении новой услуги в результирующую выборку
    # на середине прохода мы могли понять, сколько клиентов до этого эту услугу не имеет
    customer_amount = 0
    while row != "exhausted":
        customer_amount += 1
        services = row[2]
        for service in services:
            # Проверяем, записали ли мы уже какие-то данные по этой услуге
            if service in result:
                row = result[service]
                row["connected"] += 1
                # Берем словарь с данными о похожих услугах
                sims = row["sims"]
                for anotherService in services:
                    if anotherService != service:
                        if anotherService in sims:
                            sims[anotherService] += 1
                        else:
                            sims[anotherService] = 1
            # Если такой услуги еще нет, делаем для нее запись
            else:
                row = {"unconnected": 0, "connected": 1, "sims": {}}
                for anotherService in services:
                    if anotherService != service:
                        row["sims"][anotherService] = 1
                result[service] = row

        row = next(iterator, "exhausted")
    for service in result:
        result[service]["unconnected"] = customer_amount - result[service]["connected"]
    res = calculateSimilarity(result)
    return iter(res)


class TrainService(metaclass=SingletonMeta):
    """A train engine"""

    spark: SparkSession
    db: DatabaseConnector = DatabaseConnector()

    def __init__(self, sc):
        """Init train engine"""

        logger.info("Starting up the Train Engine...")
        self.spark = sc

    def train(self):
        upper = self.spark.read.format("jdbc").option("url", self.db.db_properties["url"]) \
            .option("dbtable", "(select count(DISTINCT id_customer) from ml_service.history) foo") \
            .option("user", self.db.db_properties["username"]) \
            .option("password", self.db.db_properties["password"]) \
            .option("driver", self.db.db_properties["driver"]) \
            .load().collect()[0]["count"]

        similarities: List[Similarity] = self.spark.read.format("jdbc").option("url", self.db.db_properties["url"]) \
            .option("dbtable",
                    "(select ROW_NUMBER () OVER (ORDER BY id_customer) as num, id_customer, "
                    "array_agg(code) as services from ml_service.history inner join service "
                    "on service.id = history.id_service GROUP "
                    "BY id_customer) foo") \
            .option("user", self.db.db_properties["username"]) \
            .option("password", self.db.db_properties["password"]) \
            .option("driver", self.db.db_properties["driver"]) \
            .option("numPartitions", self.db.db_properties["partitions"]) \
            .option("lowerBound", self.db.db_properties["lowerBound"]) \
            .option("upperBound", upper) \
            .option("partitionColumn", "num") \
            .load().rdd.mapPartitions(matrix).collect()

        result: dict = {}
        # Разщделять на количество агрегаций + посмотреть, точно ли агрегируется как нужно
        for sim in similarities:
            row: dict = sim.sims
            if sim.name in result:
                row = {k: result[sim.name].get(k, 0) + sim.sims.get(k, 0) for k in set(result[sim.name]) | set(sim.sims)}
            result[sim.name] = row
            for el in row:
                if row[el] > 0:
                    print(el)
                    print(row[el])
        print(result)
        df = DataFrame(result).T.fillna(0)
        epsilon = 0.3
        min_samples = 4

        db = DBSCAN(eps=epsilon, min_samples=min_samples, metric="precomputed").fit(df)
        labels = db.labels_
        print(labels.size)
        print(labels)


class Similarity:
    sims: dict

    def __init__(self, name, sims: dict):
        self.name = name
        self.sims = sims




        #.map(lambda x: (x.name, x.sims)).reduceByKey(
        #    lambda x, y: (x.get(k, 0) + y.get(k, 0) for k in set(x) | set(y))
        #)
