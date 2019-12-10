from . import ma
from .models import AADFByDirection


class AADFByDirectionSchema(ma.ModelSchema):
    class Meta:
        model = AADFByDirection


aadf_by_direction_schema = AADFByDirectionSchema()
list_aadf_by_direction_schema = AADFByDirectionSchema(many=True)
