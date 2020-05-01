import app.ml as ml
from flask import Flask


def create_app():
    app = Flask(__name__)
    ml.init_app(app)
    return app
