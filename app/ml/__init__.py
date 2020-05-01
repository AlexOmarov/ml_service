from flask import Flask

from app.ml.controllers.routes import ml

app = Flask(__name__)


def init_app(local_app):
    local_app.register_blueprint(ml)
    return local_app
