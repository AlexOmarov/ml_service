from flask import Blueprint
from app.ml.service.service import find_cloth
ml = Blueprint('ml', __name__)


@ml.route('/')
def home():
    find_cloth()
    return "This is an example ml"
