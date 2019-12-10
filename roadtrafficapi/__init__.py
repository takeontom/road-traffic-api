from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = "postgresql://roadtrafficapi:roadtrafficapi@localhost:5444/roadtrafficapi"

    db.init_app(app)
    Migrate(app, db)

    return app
