from app.modules.ml.controllers.routes import ml


def init(app):
    app.register_blueprint(ml)

