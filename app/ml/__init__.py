from app.ml.controllers.routes import ml
from app.ml.service.recommendation_service import RecommendationService
from app.ml.service.train_service import TrainService



def init_app(local_app, sc):
    local_app.register_blueprint(ml)
    TrainService(sc).train()
    RecommendationService(sc)
    return local_app
