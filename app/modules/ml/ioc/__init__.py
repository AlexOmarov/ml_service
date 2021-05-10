from commons.ioc.ioc_container import IocContainer

from app.modules.ml.ioc.service.train_service import TrainService
from app.modules.ml.ioc.scheduler.train_scheduler import TrainScheduler
from app.modules.ml.ioc.service.route_handler import RouteHandler
from app.modules.ml.ioc.service.recommendation_service import RecommendationService


container = IocContainer()


def init(spark, db):
    pass
    service = TrainService(spark)
    rs = RecommendationService(spark, db)
    container.set_bean(type(TrainService).__class__.__name__, service)
    container.set_bean(type(RecommendationService).__class__.__name__, RecommendationService(spark, db))
    container.set_bean(type(TrainScheduler).__class__.__name__, TrainScheduler(service))
    container.set_bean(type(RouteHandler).__class__.__name__, RouteHandler(rs))
