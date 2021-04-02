import logging
from collections import Sequence

from pyspark.rdd import RDD
from pyspark.sql import SparkSession, GroupedData, DataFrame
from pyspark.sql.functions import collect_set

from app.commons.db.database_connector import DatabaseConnector
from app.commons.singleton.singleton_meta import SingletonMeta
from sklearn.cluster import DBSCAN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def calculateSimilarity(history):
    result = {}
    for service in history.keys():
        for anotherService in history.keys():
            if service != anotherService:
                for sim in history[service]["sims"].keys():
                    if sim == anotherService:
                        res = history[service]["sims"][sim] - history[anotherService]["sims"][service]
                        print(service + " " + anotherService + "=" + str(res))
    return history


# def matrix(iterator) -> dict:
#    result = {}
#    row = next(iterator, "exhausted")
#    while row != "exhausted":
#       id_service = row[0]
#        id_customer = row[1]
#        if id_service in result:
#            result[id_service] = result[id_service] + id_customer
#        else:
#            result[id_service] = id_customer
#        row = next(iterator, "exhausted")
#    res = calculateSimilarity(result)
#    return result


def matrix(iterator) -> dict:
    print("MATRIX!!!")
    result = {}
    row = next(iterator, "exhausted")
    # работает как индекс для итератора. Нужен для того, чтобы при добавлении новой услуги в результирующую выборку
    # на середине прохода мы могли понять, сколько клиентов до этого эту услугу не имеет
    customer_amount = 0
    while row != "exhausted":
        customer_amount += 1
        customer = row[1]
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
    return res


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

        history = self.spark.read.format("jdbc").option("url", self.db.db_properties["url"]) \
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
            .load().rdd
        distance_matrix = self.calculateMatrix(history)
        distance_matrix.foreach(lambda p: p)
        epsilon = 0.3
        min_samples = 3

        # db = DBSCAN(eps=epsilon, min_samples=min_samples, metric="precomputed").fit([[1, 2, 3], [1, 2, 3], [1, 2, 3]])
        # labels = db.labels_

    def calculateMatrix(self, history: RDD):
        # return history.flatMap(lambda row: [(w, [row[1]]) for w in row[2]]).mapPartitions(matrix)
        return history.mapPartitions(matrix)
