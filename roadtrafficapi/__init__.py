from flask import Flask
from flask_compress import Compress
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
    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = "postgresql://roadtrafficapi:roadtrafficapi@localhost:5444/roadtrafficapi"

    db.init_app(app)
    ma.init_app(app)

    # Enable alembic migration functionality
    Migrate(app, db)

    # Import models so alembic can pick them up for migrations
    import roadtrafficapi.models

    # Enable GZipped responses
    compress.init_app(app)

    return app
