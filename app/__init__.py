from flask import Flask

from app.config import Config
from app.database import db
from app.utils.logging_config import configure_logging


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_mapping(
        SQLALCHEMY_DATABASE_URI=Config.DATABASE_URL,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    if test_config:
        app.config.update(test_config)

    configure_logging()

    db.init_app(app)

    from app.models import Alert, Metric
    from app.routes import api

    app.register_blueprint(api, url_prefix="/api")

    with app.app_context():
        db.create_all()

    return app
