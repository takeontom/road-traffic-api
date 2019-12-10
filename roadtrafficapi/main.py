from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from . import create_app

app = create_app()


@app.route("/")
def hello():
    return "Hi."
