import click
from flask import Flask, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from . import create_app
from .importers import import_aadf_by_direction
from .models import AADFByDirection
from .schemas import aadf_by_direction_schema, list_aadf_by_direction_schema

app = create_app()


@app.cli.command("import-aadf-by-direction")
@click.argument("local_authority_id")
def cmd_import_aadf_by_direction(local_authority_id):
    """
    Import AADF By Direction data for a specific local authority.

    See https://roadtraffic.dft.gov.uk/local-authorities/ for IDs.
    """
    import_aadf_by_direction(local_authority_id)


@app.route("/api/by-direction/", methods=["GET"])
def aadf_by_direction_list():
    """
    Display all AADF By Direction records.
    """
    page = request.args.get("page", 1, type=int)
    per_page = 1000

    pagination = AADFByDirection.query.paginate(page, per_page, False)

    all_aadf_by_directions = pagination.items

    return {
        "data": list_aadf_by_direction_schema.dump(all_aadf_by_directions),
        "meta": {
            "page": page,
            "per_page": per_page,
            "pages": pagination.pages,
            "total": pagination.total,
        },
    }
