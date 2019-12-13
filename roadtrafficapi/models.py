from geoalchemy2 import Geometry

from . import db


class Ward(db.Model):
    """
    Represents a single UK ward, as defined by gov.uk's dataset.

    Source data is from: https://data.gov.uk/dataset/dde6c09f-06d1-4bbe-a328-d1ef2b52e167/wards-december-2016-full-clipped-boundaries-in-great-britain

    Table structure defined by the `shp2pgsql` tool, which converts a .shp
    file into SQL CREATE TABLE and INSERT statements.

    Model is not managed by alembic so does not have migrations. Instead create
    table using the `shp2pgsql` tool as per: https://gis.stackexchange.com/questions/41799/adding-shapefiles-to-postgis-database
    """

    __tablename__ = "wards"

    gid = db.Column(db.Integer, primary_key=True)
    objectid = db.Column(db.BigInteger)
    wd16cd = db.Column(db.String(length=80))
    wd16nm = db.Column(db.String(length=80))
    wd16nmw = db.Column(db.String(length=80))
    lad16cd = db.Column(db.String(length=80))
    lad16nm = db.Column(db.String(length=80))
    bng_e = db.Column(db.BigInteger)
    bng_n = db.Column(db.BigInteger)
    long = db.Column(db.Numeric)
    lat = db.Column(db.Numeric)
    st_areasha = db.Column(db.Numeric)
    st_lengths = db.Column(db.Numeric)
    geom = db.Column(Geometry(geometry_type="MULTIPOLYGON", srid=4326))


class AADFByDirection(db.Model):
    """
    Represents a single row of the AADF By Direction data set.

    Data could potentially be normalised somewhat (separate models for regions
    and local authorities), rather than dumping into a single model like this.
    However doesn't present much benefit and just complicates things.

    If in the future more structure is needed, e.g. to store extra information
    about a local authority, then this will likely need to be refactored.
    """

    # There's not really a suitable ID in the AADF By Direction data. Choice
    # is either use a compound key (count_pount_id, year, direction) or
    # generate our own instead.
    id = db.Column(db.Integer, primary_key=True)

    count_point_id = db.Column(db.Integer, nullable=False, index=True)
    year = db.Column(db.String(length=4), nullable=False, index=True)

    region_id = db.Column(db.Integer, nullable=False, index=True)
    region_name = db.Column(db.String(length=50), nullable=False, index=True)

    local_authority_id = db.Column(db.Integer, nullable=False, index=True)
    local_authority_name = db.Column(
        db.String(length=50), nullable=False, index=True
    )

    road_name = db.Column(db.String(length=50), nullable=False, index=True)
    road_type = db.Column(db.String(length=10), nullable=False, index=True)

    start_junction_road_name = db.Column(db.String(length=100))
    end_junction_road_name = db.Column(db.String(length=100))

    easting = db.Column(db.Integer, nullable=False)
    northing = db.Column(db.Integer, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    point = db.Column(Geometry(geometry_type="POINT", srid=4326), index=True)

    # Numeric (i.e. Decimal) fields slightly complicate things during
    # [de]serialisation in Marshmallow. See warning in docs for more info:
    # https://marshmallow.readthedocs.io/en/latest/api_reference.html?highlight=function#marshmallow.fields.Decimal
    link_length_km = db.Column(db.Numeric(precision=2))
    link_length_miles = db.Column(db.Numeric(precision=2))

    estimation_method = db.Column(
        db.String(length=15), nullable=False, index=True
    )
    estimation_method_detailed = db.Column(
        db.String(length=100), nullable=False, index=True
    )
    direction_of_travel = db.Column(
        db.String(length=1), nullable=False, index=True
    )

    pedal_cycles = db.Column(db.Integer, nullable=False)
    two_wheeled_motor_vehicles = db.Column(db.Integer, nullable=False)
    cars_and_taxis = db.Column(db.Integer, nullable=False)
    buses_and_coaches = db.Column(db.Integer, nullable=False)
    lgvs = db.Column(db.Integer, nullable=False)
    hgvs_2_rigid_axle = db.Column(db.Integer, nullable=False)
    hgvs_3_rigid_axle = db.Column(db.Integer, nullable=False)
    hgvs_3_or_4_articulated_axle = db.Column(db.Integer, nullable=False)
    hgvs_4_or_more_rigid_axle = db.Column(db.Integer, nullable=False)
    hgvs_5_articulated_axle = db.Column(db.Integer, nullable=False)
    hgvs_6_articulated_axle = db.Column(db.Integer, nullable=False)
    all_hgvs = db.Column(db.Integer, nullable=False)
    all_motor_vehicles = db.Column(db.Integer, nullable=False)
