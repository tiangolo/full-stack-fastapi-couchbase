# Import standard library packages

# Import installed packages
from marshmallow import fields

# Import app code
from .base import BaseSchema


class RolesSchema(BaseSchema):
    # Own properties
    roles = fields.List(fields.Str())
