import logging

from flask import jsonify, Response, Request

from app.modules.ml import ioc
from app.modules.ml.service.recommendation_service import RecommendationService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

service: RecommendationService = ioc.get_bean(RecommendationService.__class__.__name__)


def recommend(request: Request) -> Response:
    result = service.recommend(request.get_json()["user_id"])
    return jsonify(result=[e.serialize() for e in result])
