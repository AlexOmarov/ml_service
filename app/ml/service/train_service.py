import logging

from pyspark import SparkContext
from operator import add

from app.commons.singleton.singleton_meta import SingletonMeta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrainService(metaclass=SingletonMeta):
    """A train engine"""

    spark: SparkContext

    def __init__(self, sc):
        """Init train engine
        """

        logger.info("Starting up the Train Engine...")
        self.spark = sc

    def train(self):
        print("training...")
        self.spark.range(1000 * 1000 * 500).reduce(add)
