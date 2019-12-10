from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow()


def create_app():
    app = Flask(__name__)
    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = "postgresql://roadtrafficapi:roadtrafficapi@localhost:5444/roadtrafficapi"

    db.init_app(app)
    ma.init_app(app)

    Migrate(app, db)

    import roadtrafficapi.models

    return app
