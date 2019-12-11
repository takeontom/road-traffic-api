from decimal import Decimal

from marshmallow import Schema, fields, post_dump, pre_dump, pre_load

from . import ma
from .models import AADFByDirection


class AADFByDirectionSchema(ma.ModelSchema):
    class Meta:
        model = AADFByDirection

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

        if in_data["link_length_km"] is not None:
            in_data["link_length_km"] = float(in_data["link_length_km"])

        if in_data["link_length_miles"] is not None:
            in_data["link_length_miles"] = float(in_data["link_length_miles"])

        return in_data

    @pre_load
    def decimal_link_lengths(self, in_data, **kwargs):
        # Decimal fields don't convert empty strings to a valid number or None.
        # So check for empty string and ensure None is being used.

        if in_data["link_length_miles"] == "":
            in_data["link_length_miles"] = None
        else:
            in_data["link_length_miles"] = Decimal(
                in_data["link_length_miles"]
            )

        if in_data["link_length_km"] == "":
            in_data["link_length_km"] = None
        else:
            in_data["link_length_km"] = Decimal(in_data["link_length_km"])

        return in_data


aadf_by_direction_schema = AADFByDirectionSchema()
list_aadf_by_direction_schema = AADFByDirectionSchema(many=True)


class YearSchema(Schema):
    year = fields.String()


year_schema = YearSchema()
list_year_schema = YearSchema(many=True)
