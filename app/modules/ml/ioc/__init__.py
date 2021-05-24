from app.commons.ioc.ioc_container import IocContainer

container = IocContainer()


def init(spark, db):
    from app.modules.ml.ioc.service.train_service import TrainService
    from app.modules.ml.ioc.scheduler.train_scheduler import TrainScheduler
    from app.modules.ml.ioc.service.route_handler import RouteHandler
    from app.modules.ml.ioc.service.recommendation_service import RecommendationService
    service = TrainService(spark)
    rs = RecommendationService(spark, db)
    container.set_bean(TrainService.__name__, service)
    container.set_bean(RecommendationService.__name__, RecommendationService(spark, db))
    scheduler = TrainScheduler(service)
    container.set_bean(TrainScheduler.__name__, scheduler)
    scheduler.start()
    container.set_bean(RouteHandler.__name__, RouteHandler(rs))
