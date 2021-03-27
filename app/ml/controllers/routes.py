from flask import Blueprint, request

from app.ml.service.recommendation_service import RecommendationService

service = RecommendationService()
ml = Blueprint('ml', __name__)


@ml.route('/recommend', methods=['POST'])
def recommend():
    service.recommend(request.get_json()["user_id"])
    return "This is an example ml"
