from flask import Flask, g, request

from app.config import Config
from app.database import db
from app.utils.request_id import generate_request_id
from app.utils.logging_config import configure_logging
from app.docs import configure_swagger


def create_app(test_config=None):
    app = Flask(__name__)

    @app.before_request
    def assign_request_id():
        g.request_id = request.headers.get(
            "X-Request-ID",
            generate_request_id(),
        )

    @app.after_request
    def add_request_id(response):
        response.headers["X-Request-ID"] = g.request_id
        return response

    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=Config.DATABASE_URL,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config:
        app.config.update(test_config)

    configure_logging()
    configure_swagger(app)

    db.init_app(app)

    from app.models import Alert, Metric
    from app.routes import api

    app.register_blueprint(api, url_prefix="/api")

    with app.app_context():
        db.create_all()

    return app
