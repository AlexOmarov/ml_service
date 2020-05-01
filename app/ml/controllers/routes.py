from flask import Blueprint

ml = Blueprint('ml', __name__)


@ml.route('/')
def index():
    return "This is an example ml"
