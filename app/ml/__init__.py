from app.ml.controllers.routes import ml


def init_app(local_app):
    local_app.register_blueprint(ml)
    return local_app
