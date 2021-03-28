# Import spark
import logging
from typing import List

from pyspark import SparkContext

from app.commons.dto.recommendation import Recommendation
from app.commons.singleton.singleton_meta import SingletonMeta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RecommendationService(metaclass=SingletonMeta):
    """A recommendation engine"""

    spark: SparkContext

    def __init__(self, sc):
        """Init the recommendation engine given a Spark context and a dataset path
        """

        logger.info("Starting up the Recommendation Engine: ")
        self.spark = sc

    def recommend(self, user_id: int) -> List[Recommendation]:
        self.spark.parallelize([user_id, user_id, user_id, user_id, user_id]).collect()
        result = [Recommendation(service="", rate=0.001), Recommendation(service="", rate=0.001),
                  Recommendation(service="", rate=0.001)]
        return result
