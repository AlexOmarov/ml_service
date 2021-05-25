import logging
from typing import List

from pandas import *
from pyspark.sql import SparkSession
from sklearn.cluster import DBSCAN

from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Similarity:
    sims: dict

    def __init__(self, name, sims: dict):
        self.name = name
        self.sims = sims


class TrainService:
    spark: SparkSession

    def __init__(self, sc):
        self.spark = sc

    def train(self):
        similarities: List[Similarity] = self.getData()

        result: dict = {}
        aggregation_count = {}
        # Разделять на количество агрегаций + посмотреть, точно ли агрегируется как нужно
        for sim in similarities:
            row: dict = sim.sims
            if sim.name in result:
                row = {k: result[sim.name].get(k, 0) + sim.sims.get(k, 0) for k in
                       set(result[sim.name]) | set(sim.sims)}
                if sim.name in aggregation_count:
                    aggregation_count[sim.name] += 1
                else:
                    aggregation_count[sim.name] = 1
            result[sim.name] = row
        for service in aggregation_count:
            for sim in result[service]:
                result[service][sim] = result[service][sim] / aggregation_count[service]
        df = DataFrame(result).T.fillna(0)
        epsilon = 0.09
        min_samples = 3

        if df.size < 1:
            print("df is empty")
        else:
            print(df)
            db = DBSCAN(eps=epsilon, min_samples=min_samples, metric="precomputed").fit(df)
            labels = db.labels_
            # TODO: Store trained model

            print(labels.size)
            print(labels)

    def getData(self) -> List[Similarity]:
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
            .load().rdd.mapPartitions(matrix).collect()


def calculateSimilarity(history):
    result = []
    for service in history:
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

        result.append(Similarity(service, row))
    return result


def matrix(iterator):
    result = {}
    row = next(iterator, "exhausted")
    # работает как индекс для итератора. Нужен для того, чтобы при добавлении новой услуги в результирующую выборку
    # на середине прохода мы могли понять, сколько клиентов до этого эту услугу не имеет
    customer_amount = 0
    while row != "exhausted":
        customer_amount += 1
        services = row[1].replace('\'', '').replace('[', '').replace(']', '').split(',')
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
