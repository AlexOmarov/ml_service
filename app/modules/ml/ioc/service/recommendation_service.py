# Import spark



class Recommendation:
    service: str
    rate: float

    # parameterized constructor
    def __init__(self, service, rate):
        self.service = service
        self.rate = rate

    def serialize(self):
        return {
            'service': self.service,
            'rate': self.rate
        }


class RecommendationService:
    """A recommendation engine"""



    def __init__(self, sc, db):
        """Init the recommendation engine given a Spark context and a dataset path
        """


        self.spark = sc
        self.db = db


