class Recommendation:
    service: str
    rate: float

    def __init__(self, service, rate):
        self.service = service
        self.rate = rate

    def serialize(self):
        return {
            'service': self.service,
            'rate': self.rate
        }

