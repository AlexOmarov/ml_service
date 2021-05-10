import app.modules.ml.ioc as ioc
import app.modules.ml.controllers as controllers


def init(app, spark, db):
    ioc.init(spark, db)
    controllers.init(app)
