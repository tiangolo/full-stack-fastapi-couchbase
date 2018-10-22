# -*- coding: utf-8 -*-

# Import standard library packages

# Import installed packages
from marshmallow import fields

# Import app code
from .base import BaseSchema


class UserSchema(BaseSchema):
    # Own properties
    type = fields.Str()
    name = fields.Str()
    human_name = fields.Str()
    email = fields.Str()
    admin_roles = fields.List(fields.Str())
    admin_channels = fields.List(fields.Str())
    disabled = fields.Boolean()
