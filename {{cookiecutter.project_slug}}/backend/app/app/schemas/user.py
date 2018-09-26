# -*- coding: utf-8 -*-

# Import standard library packages

# Import installed packages
from marshmallow import fields

# Import app code
from .base import BaseSchema


class UserSchema(BaseSchema):
    # Own properties
    _id = fields.Str()
    _rev = fields.Str()
    name = fields.Str()
    type = fields.Str()
    roles = fields.List(fields.Str())
