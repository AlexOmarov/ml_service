def init(app):
    from app.modules.ml.controllers.routes import ml
    app.register_blueprint(ml)

