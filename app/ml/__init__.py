from app.ml.controllers.routes import ml
from app.ml.service.recommendation_service import RecommendationService


def init_app(local_app):
    local_app.register_blueprint(ml)
    return local_app
