from flask import Blueprint, request

from modules.ml.controllers.route_handler import recommend

ml = Blueprint('ml', __name__)


@ml.route('/recommend', methods=['POST'])
def recommend():
    return recommend(request)
