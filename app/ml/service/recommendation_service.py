# Import spark
from pyspark.sql import SparkSession
from pyspark import SparkContext

import logging

from app.commons.singleton.singleton_meta import SingletonMeta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecommendationService(metaclass=SingletonMeta):
    """A movie recommendation engine"""

    spark: SparkContext

    def __init__(self):
        """Init the recommendation engine given a Spark context and a dataset path
        """

        logger.info("Starting up the Recommendation Engine: ")
        var = SparkSession.builder
        spark = SparkSession.builder.master("local[*]").appName("ml").getOrCreate()
        sc = spark.sparkContext
        sc.setLogLevel("INFO")
        self.spark = sc

        # Load ratings data for later use
        logger.info("Loading Ratings data...")

    def recommend(self, user_id: int):
        result = self.spark.parallelize(user_id).name()
        print("recommend for " + result)
