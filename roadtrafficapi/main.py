import click
from flask import Flask, request
from flask_apispec import FlaskApiSpec, doc, marshal_with, use_kwargs
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from webargs import fields

from . import create_app
from .importers import import_aadf_by_direction
from .models import AADFByDirection
from .schemas import (
    list_aadf_by_direction_schema,
    list_local_authority_schema,
    list_region_schema,
    list_road_schema,
    list_road_type_schema,
    list_year_schema,
)

app = create_app()


@app.cli.command("import-aadf-by-direction")
@click.argument("local_authority_id")
def cmd_import_aadf_by_direction(local_authority_id):
    """
    Import AADF By Direction data for a specific local authority.

    See https://roadtraffic.dft.gov.uk/local-authorities/ for IDs.
    """
    import_aadf_by_direction(local_authority_id)


def generate_pagination_meta(pagination):
    """
    Helper function to generate pagination meta data.
    """
    return {
        "meta": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "pages": pagination.pages,
            "total": pagination.total,
        }
    }


def generate_response(data, pagination):
    """
    Helper function to help ensure all responses follow the same structure.
    """
    out = {"data": data}

    out.update(generate_pagination_meta(pagination))

    return out


@app.route("/api/by-direction/", methods=["GET"])
@use_kwargs({"page": fields.Int(location="query", required=False, missing=1)})
def aadf_by_direction_list(**kwargs):
    """
    List all AADF By Direction records.
    """
    page = kwargs["page"]
    per_page = 1000

    pagination = AADFByDirection.query.paginate(page, per_page, False)

    all_aadf_by_directions = pagination.items

    data = list_aadf_by_direction_schema.dump(all_aadf_by_directions)

    return generate_response(data, pagination)


@app.route("/api/by-direction/year/", methods=["GET"])
@use_kwargs({"page": fields.Int(location="query", required=False, missing=1)})
def year_list(**kwargs):
    """
    List all years with AADF By Direction records.
    """
    page = kwargs["page"]
    per_page = 1000

    pagination = (
        AADFByDirection.query.with_entities(AADFByDirection.year)
        .group_by(AADFByDirection.year)
        .order_by(AADFByDirection.year)
        .paginate(page, per_page, False)
    )
    all_years = list_year_schema.dump(pagination.items)

    return generate_response(all_years, pagination)


@app.route("/api/by-direction/region/", methods=["GET"])
@use_kwargs({"page": fields.Int(location="query", required=False, missing=1)})
def region_list(**kwargs):
    """
    List all regions in AADF By Direction records.
    """
    page = kwargs["page"]
    per_page = 1000

    pagination = (
        AADFByDirection.query.with_entities(
            AADFByDirection.region_id, AADFByDirection.region_name
        )
        .group_by(AADFByDirection.region_id, AADFByDirection.region_name)
        .order_by(AADFByDirection.region_id)
        .paginate(page, per_page, False)
    )
    all_regions = list_region_schema.dump(pagination.items)

    return generate_response(all_regions, pagination)


@app.route("/api/by-direction/local-authority/", methods=["GET"])
@use_kwargs({"page": fields.Int(location="query", required=False, missing=1)})
def local_authority_list(**kwargs):
    """
    List all regions in AADF By Direction records.
    """
    page = kwargs["page"]
    per_page = 1000

    pagination = (
        AADFByDirection.query.with_entities(
            AADFByDirection.region_id,
            AADFByDirection.region_name,
            AADFByDirection.local_authority_id,
            AADFByDirection.local_authority_name,
        )
        .group_by(
            AADFByDirection.local_authority_id,
            AADFByDirection.local_authority_name,
            AADFByDirection.region_id,
            AADFByDirection.region_name,
        )
        .order_by(AADFByDirection.local_authority_id)
        .paginate(page, per_page, False)
    )
    all_regions = list_local_authority_schema.dump(pagination.items)

    return generate_response(all_regions, pagination)


@app.route("/api/by-direction/road/", methods=["GET"])
@use_kwargs({"page": fields.Int(location="query", required=False, missing=1)})
def road_list(**kwargs):
    """
    List all roads in AADF By Direction records.

    Be aware that road names are not unique. E.g. there's an A379 in Plymouth
    and Exeter, completely unconnected to one another. So when using road names
    for filters, make sure to also filter by local authority or by spatial
    query.
    """
    page = kwargs["page"]
    per_page = 1000

    pagination = (
        AADFByDirection.query.with_entities(
            AADFByDirection.road_name, AADFByDirection.road_type,
        )
        .group_by(AADFByDirection.road_name, AADFByDirection.road_type,)
        .order_by(AADFByDirection.road_name)
        .paginate(page, per_page, False)
    )
    all_roads = list_road_schema.dump(pagination.items)

    return generate_response(all_roads, pagination)


@app.route("/api/by-direction/road-type/", methods=["GET"])
@use_kwargs({"page": fields.Int(location="query", required=False, missing=1)})
def road_type_list(**kwargs):
    """
    List all roads types in AADF By Direction records.
    """
    page = kwargs["page"]
    per_page = 1000

    pagination = (
        AADFByDirection.query.with_entities(AADFByDirection.road_type)
        .group_by(AADFByDirection.road_type)
        .order_by(AADFByDirection.road_type)
        .paginate(page, per_page, False)
    )
    all_road_types = list_road_type_schema.dump(pagination.items)

    return generate_response(all_road_types, pagination)


docs = FlaskApiSpec(app)
docs.register(aadf_by_direction_list)
docs.register(year_list)
docs.register(region_list)
docs.register(local_authority_list)
docs.register(road_list)
docs.register(road_type_list)
