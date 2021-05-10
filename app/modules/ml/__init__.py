import sys

from app.modules.ml.controllers.routes import ml
from app.modules.ml.scheduler.train_scheduler import TrainScheduler
from app.modules.ml.service.recommendation_service import RecommendationService
from app.modules.ml.service.train_service import TrainService
from commons.ioc.ioc_container import IocContainer

# this is a pointer to the module object instance itself.
from modules.ml.controllers.route_handler import RouteHandler

this = sys.modules[__name__]

# we can explicitly make assignments on it
this.ioc = IocContainer()


def init(app, spark, db):
    create_beans(spark, db)
    app.register_blueprint(ml)


def create_beans(spark, db):
    this.ioc.set_bean(TrainService.__class__.__name__, TrainService(spark))
    this.ioc.set_bean(RecommendationService.__class__.__name__, RecommendationService(spark, db))
    this.ioc.set_bean(TrainScheduler.__class__.__name__, TrainScheduler())
    this.ioc.set_bean(RouteHandler.__class__.__name__, RouteHandler())

