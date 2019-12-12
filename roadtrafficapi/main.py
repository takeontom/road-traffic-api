import click
from flask import Flask, request
from flask_apispec import FlaskApiSpec, doc, marshal_with, use_kwargs
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from webargs import fields

from . import create_app
from .importers import import_aadf_by_direction
from .models import AADFByDirection, Ward
from .schemas import (
    list_aadf_by_direction_schema,
    list_estimation_method_schema,
    list_local_authority_schema,
    list_region_schema,
    list_road_schema,
    list_road_type_schema,
    list_ward_schema,
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


def generate_response(data, pagination, query=None):
    """
    Helper function to help ensure all responses follow the same structure.
    """
    out = {"data": data}

    out.update(generate_pagination_meta(pagination))

    out["query"] = query

    return out


@app.route("/api/by-direction/", methods=["GET"])
@use_kwargs({"page": fields.Int(location="query", required=False, missing=1)})
@use_kwargs({"year": fields.String(location="query", required=False)})
@use_kwargs(
    {"local_authority_id": fields.Int(location="query", required=False)}
)
@use_kwargs({"region_id": fields.Int(location="query", required=False)})
@use_kwargs({"road_name": fields.String(location="query", required=False)})
@use_kwargs({"road_type": fields.String(location="query", required=False)})
@use_kwargs(
    {"direction_of_travel": fields.String(location="query", required=False)}
)
@use_kwargs(
    {"estimation_method": fields.String(location="query", required=False)}
)
@use_kwargs(
    {
        "estimation_method_detailed": fields.String(
            location="query", required=False
        )
    }
)
@use_kwargs(
    {"longitude": fields.Float(location="query", required=False, missing=None)}
)
@use_kwargs(
    {"latitude": fields.Float(location="query", required=False, missing=None)}
)
@use_kwargs(
    {"distance": fields.Float(location="query", required=False, missing=1000)}
)
def aadf_by_direction_list(page, longitude, latitude, distance, **kwargs):
    """
    List all AADF By Direction records.
    """
    per_page = 1000

    # Some query params are simply mappings from input, some require some
    # logic, e.g. combining long/lat into a point, so build up the query
    # piece by piece
    q = AADFByDirection.query

    # Find AADF records by longitude and latitude, with a configurable distance
    if longitude and latitude:
        q = q.filter(
            AADFByDirection.point.ST_Distance_Sphere(
                f"SRID=4326;POINT({longitude} {latitude})"
            )
            <= distance
        )

    # Unpack the rest of the query params into the filter
    q = q.filter_by(**kwargs)

    # Throw the built up query into the paginator
    pagination = q.paginate(page, per_page, False)

    all_aadf_by_directions = pagination.items

    data = list_aadf_by_direction_schema.dump(all_aadf_by_directions)

    query = {
        "longitude": longitude,
        "latitude": latitude,
        "distance": distance,
        **kwargs,
    }

    return generate_response(data, pagination, query)


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


@app.route("/api/by-direction/estimation-method/", methods=["GET"])
@use_kwargs({"page": fields.Int(location="query", required=False, missing=1)})
def estimation_method_list(**kwargs):
    """
    List all estimation methods in AADF By Direction records.
    """
    page = kwargs["page"]
    per_page = 1000

    pagination = (
        AADFByDirection.query.with_entities(
            AADFByDirection.estimation_method,
            AADFByDirection.estimation_method_detailed,
        )
        .group_by(
            AADFByDirection.estimation_method,
            AADFByDirection.estimation_method_detailed,
        )
        .order_by(AADFByDirection.estimation_method)
        .paginate(page, per_page, False)
    )
    all_estimation_methods = list_estimation_method_schema.dump(
        pagination.items
    )

    return generate_response(all_estimation_methods, pagination)


@app.route("/api/ward/", methods=["GET"])
@use_kwargs({"page": fields.Int(location="query", required=False, missing=1)})
def ward_list(**kwargs):
    """
    List all wards.
    """
    page = kwargs["page"]
    per_page = 100

    pagination = Ward.query.order_by(Ward.gid).paginate(page, per_page, False)
    all_wards = list_ward_schema.dump(pagination.items)

    return generate_response(all_wards, pagination)


docs = FlaskApiSpec(app)
docs.register(aadf_by_direction_list)
docs.register(year_list)
docs.register(region_list)
docs.register(local_authority_list)
docs.register(road_list)
docs.register(road_type_list)
docs.register(estimation_method_list)

docs.register(ward_list)
