from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask import Flask
from flask_compress import Compress
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Use Marshmallow for [de]serialisation. Works nicely with SQLAlchemy models
# and handles a bit of complexity for us.
ma = Marshmallow()

# GZip responses
compress = Compress()


def create_app():
    app = Flask(__name__)
    app.config.update(
        {
            "SQLALCHEMY_DATABASE_URI": "postgresql://roadtrafficapi:roadtrafficapi@localhost:5444/roadtrafficapi",
            "APISPEC_SPEC": APISpec(
                title="Road Traffic API",
                version="1",
                openapi_version="2.0",
                plugins=[MarshmallowPlugin()],
            ),
            "APISPEC_SWAGGER_URL": "/api/json/",
            "APISPEC_SWAGGER_UI_URL": "/api/",
        }
    )

    db.init_app(app)
    ma.init_app(app)

    # Enable alembic migration functionality
    Migrate(app, db)

    # Import models so alembic can pick them up for migrations
    import roadtrafficapi.models

    # Enable GZipped responses
    compress.init_app(app)

    # Allow requests from all domains for all routes.
    CORS(app)

    return app
