from flask import Blueprint, request

from app.modules.ml.ioc.service.route_handler import RouteHandler
from app.modules.ml.ioc import container

ml = Blueprint('ml', __name__)


@ml.route('/recommend', methods=['POST'])
def recommend():
    handler: RouteHandler = container.get_bean(RouteHandler.__name__)
    return handler.recommend(request)
