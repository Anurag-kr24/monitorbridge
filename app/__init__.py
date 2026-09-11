import logging
import time

from flask import Flask, g, request

from app.config import Config
from app.database import db
from app.utils.request_id import generate_request_id
from app.utils.logging_config import configure_logging, RequestContextFilter
from app.docs import configure_swagger


logger = logging.getLogger("monitorbridge.request")


def create_app(test_config=None):
    app = Flask(__name__)

    @app.before_request
    def assign_request_id():
        g.request_start = time.perf_counter()
        g.request_id = request.headers.get(
            "X-Request-ID",
            generate_request_id(),
        )

    @app.after_request
    def add_request_id(response):
        response.headers["X-Request-ID"] = g.request_id
        duration_ms = (time.perf_counter() - g.request_start) * 1000
        logger.info(
            "%s %s | status=%s | duration_ms=%.2f",
            request.method,
            request.path,
            response.status_code,
            duration_ms,
        )
        return response

    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=Config.DATABASE_URL,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config:
        app.config.update(test_config)

    configure_logging()
    logging.getLogger().addFilter(RequestContextFilter())
    configure_swagger(app)

    db.init_app(app)

    from app.models import Alert, Metric
    from app.routes import api

    app.register_blueprint(api, url_prefix="/api")

    with app.app_context():
        db.create_all()

    return app
