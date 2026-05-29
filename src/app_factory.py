from flask import Flask

from src.proxy_controller import proxy_blueprint


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(proxy_blueprint)
    return app
