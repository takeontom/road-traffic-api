import click
from flask import Flask, redirect, request
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


@app.route("/")
def home():
    return redirect("/api/", 302)


aadf_by_direction_list_desc = """
# Example
To show records for counts of vehicles going North in 2018, within 3km of Exeter:

    /api/by-direction/?longitude=-3.5339&latitude=50.7184&distance=3000&year=2018&direction_of_travel=N

# Params

Most params map directly to the column names used in the data set, see
http://data.dft.gov.uk.s3.amazonaws.com/road-traffic/all-traffic-data-metadata.pdf
for a description of their purpose.

Use the other endpoints to discover possible values to use in the params.

## Spatial Searches

Setting both the `longitude` and `latitude` params will find AADF By Direction
records within a radius of that point.

The optional `distance` param defines the radius around the search point in metres.
`distance` defaults to 1000 (1km).

## Ward Searches

Ward data from https://data.gov.uk/dataset/dde6c09f-06d1-4bbe-a328-d1ef2b52e167/wards-december-2016-full-clipped-boundaries-in-great-britain
has been imported, allowing you to find AADF By Direction records within Wards.

Use the optional `ward_gid` param to do this.

# Pagination

Results are paginated, showing 1,000 records per page.

Use the `page` param to define the page number, and the `meta` collection in
response to know how many pages (and total results) there are.
"""


@app.route("/api/by-direction/", methods=["GET"])
@doc(
    summary="Paginated list of AADF By Direction records with optional filters",
    description=aadf_by_direction_list_desc,
)
@use_kwargs({"page": fields.Int(location="query", required=False)})
@use_kwargs({"count_point_id": fields.Int(location="query", required=False)})
@use_kwargs({"year": fields.String(location="query", required=False)})
@use_kwargs(
    {"local_authority_id": fields.Int(location="query", required=False)}
)
@use_kwargs(
    {"local_authority_name": fields.String(location="query", required=False)}
)
@use_kwargs({"region_id": fields.Int(location="query", required=False)})
@use_kwargs({"region_name": fields.String(location="query", required=False)})
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
@use_kwargs({"longitude": fields.Float(location="query", required=False)})
@use_kwargs({"latitude": fields.Float(location="query", required=False)})
@use_kwargs({"distance": fields.Float(location="query", required=False)})
@use_kwargs({"ward_gid": fields.Int(location="query", required=False)})
def aadf_by_direction_list(**kwargs):
    """
    List all AADF By Direction records.
    """
    per_page = 1000

    # Only used for annotating response
    query_params = {**kwargs}

    # Some args we need to do some processing on, so pop them out.
    # The rest of kwargs is used to populate the `filter_by`
    page = kwargs.pop("page", None)
    longitude = kwargs.pop("longitude", None)
    latitude = kwargs.pop("latitude", None)
    distance = kwargs.pop("distance", 1000)
    ward_gid = kwargs.pop("ward_gid", None)

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

    # Spatial join based on the Ward ID.
    if ward_gid:
        # This might be better as a relationship rather than using an ON clause
        q = q.join(Ward, Ward.geom.ST_Contains(AADFByDirection.point))
        q = q.filter(Ward.gid == ward_gid)

    # Throw the built up query into the paginator
    pagination = q.paginate(page, per_page, False)

    all_aadf_by_directions = pagination.items

    data = list_aadf_by_direction_schema.dump(all_aadf_by_directions)

    return generate_response(data, pagination, query_params)


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

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
