from decimal import Decimal

from geoalchemy2.elements import WKTElement
from geoalchemy2.types import Geometry as GeometryType
from marshmallow import Schema, fields, post_dump, pre_dump, pre_load
from marshmallow_sqlalchemy.convert import ModelConverter as BaseModelConverter
from shapely import wkb

from . import ma
from .models import AADFByDirection, Ward


class ModelConverter(BaseModelConverter):
    SQLA_TYPE_MAPPING = {
        **BaseModelConverter.SQLA_TYPE_MAPPING,
        **{GeometryType: fields.Field},
    }


class AADFByDirectionSchema(ma.ModelSchema):
    class Meta:
        model = AADFByDirection
        model_converter = ModelConverter

    @post_dump
    def point_to_string(self, in_data, **kwargs):
        if in_data["point"] is not None:
            p = wkb.loads(str(in_data["point"]), hex=True)
            in_data["point"] = str(p)
        return in_data

    @post_dump
    def decimal_link_lengths_to_float(self, in_data, **kwargs):
        # Decimal fields are not serialisable as JSON, so convert them to float
        # first. Is a known limitation of Marshmallow:
        # https://marshmallow.readthedocs.io/en/latest/api_reference.html?highlight=function#marshmallow.fields.Decimal
        #
        # Other alternatives:
        #   * Use simplejson to convert dict to json in routes.
        #   * Use the "as_string" flag on the field to serialise as string
        #     rather than Decimal and let client deal with str to decimal
        #     conversion.
        decimal_fields = ["link_length_km", "link_length_miles"]
        for field in decimal_fields:
            if in_data[field] is not None:
                in_data[field] = float(in_data[field])

        return in_data

    @pre_load
    def decimal_link_lengths(self, in_data, **kwargs):
        # Decimal fields don't convert empty strings to a valid number or None.
        # So check for empty string and ensure None is being used.
        decimal_fields = ["link_length_km", "link_length_miles"]
        for field in decimal_fields:
            if in_data[field] == "":
                in_data[field] = None
            else:
                in_data[field] = Decimal(in_data[field])

        return in_data

    @pre_load
    def create_point(self, in_data, **kwargs):
        if in_data["longitude"] and in_data["latitude"]:
            in_data[
                "point"
            ] = f'SRID=4326;POINT({in_data["longitude"]} {in_data["latitude"]})'
        return in_data


aadf_by_direction_schema = AADFByDirectionSchema()
list_aadf_by_direction_schema = AADFByDirectionSchema(many=True)


class YearSchema(Schema):
    year = fields.String()


year_schema = YearSchema()
list_year_schema = YearSchema(many=True)


class RegionSchema(Schema):
    region_id = fields.Int()
    region_name = fields.String()


region_schema = RegionSchema
list_region_schema = RegionSchema(many=True)


class LocalAuthoritySchema(Schema):
    local_authority_id = fields.Int()
    local_authority_name = fields.String()

    # Presuming a local authority is only ever in a single region
    region_id = fields.Int()
    region_name = fields.String()


local_authority_schema = LocalAuthoritySchema
list_local_authority_schema = LocalAuthoritySchema(many=True)


class RoadSchema(Schema):
    # Roads can span multiple regions and local authorities. Also road names
    # are not unique (e.g. there's A roads in Exeter with the same name as
    # roads in Plymouth), so all we can spit out per road is name and type.
    road_name = fields.String()
    road_type = fields.String()


road_schema = RoadSchema
list_road_schema = RoadSchema(many=True)


class RoadTypeSchema(Schema):
    road_type = fields.String()


road_type_schema = RoadTypeSchema
list_road_type_schema = RoadTypeSchema(many=True)


class EstimationMethodSchema(Schema):
    estimation_method = fields.String()
    estimation_method_detailed = fields.String()


estimation_method_schema = EstimationMethodSchema
list_estimation_method_schema = EstimationMethodSchema(many=True)


class WardSchema(ma.ModelSchema):
    class Meta:
        model = Ward
        model_converter = ModelConverter

    @post_dump
    def geom_to_string(self, in_data, **kwargs):
        if in_data["geom"] is not None:
            p = wkb.loads(str(in_data["geom"]), hex=True)
            in_data["geom"] = str(p)
        return in_data

    @post_dump
    def decimal_link_lengths_to_float(self, in_data, **kwargs):
        # Decimal fields are not serialisable as JSON, so convert them to float
        # first. Is a known limitation of Marshmallow:
        # https://marshmallow.readthedocs.io/en/latest/api_reference.html?highlight=function#marshmallow.fields.Decimal
        #
        # Other alternatives:
        #   * Use simplejson to convert dict to json in routes.
        #   * Use the "as_string" flag on the field to serialise as string
        #     rather than Decimal and let client deal with str to decimal
        #     conversion.
        decimal_fields = ["long", "lat", "st_areasha", "st_lengths"]
        for field in decimal_fields:
            if in_data[field] is not None:
                in_data[field] = float(in_data[field])

        return in_data


ward_schema = WardSchema
list_ward_schema = WardSchema(many=True)
