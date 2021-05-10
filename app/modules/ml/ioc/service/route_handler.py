import logging

from flask import jsonify, Response, Request

from app.modules.ml.ioc.service.recommendation_service import RecommendationService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RouteHandler:
    service: RecommendationService

    def __init__(self, service):
        self.service = service

    def recommend(self, request: Request) -> Response:
        result = self.service.recommend(request.get_json()["user_id"])
        return jsonify(result=[e.serialize() for e in result])
