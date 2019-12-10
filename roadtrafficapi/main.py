from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from . import create_app
from .models import AADFByDirection
from .schemas import aadf_by_direction_schema, list_aadf_by_direction_schema

app = create_app()


@app.route("/api/by-direction/", methods=["GET"])
def aadf_by_direction_list():
    all_aadf_by_directions = AADFByDirection.query.all()
    return {"data": list_aadf_by_direction_schema.dump(all_aadf_by_directions)}
