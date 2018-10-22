# -*- coding: utf-8 -*-

# Import standard library packages

# Import installed packages
from marshmallow import fields

# Import app code
from .base import BaseSchema


class RoleSchema(BaseSchema):
    # Own properties
    name = fields.Str()
