from flask import Blueprint, request, jsonify

from app.ml.service.recommendation_service import RecommendationService

ml = Blueprint('ml', __name__)


@ml.route('/recommend', methods=['POST'])
def recommend():
    service = RecommendationService(None)
    result = service.recommend(request.get_json()["user_id"])
    return jsonify(result=[e.serialize() for e in result])
