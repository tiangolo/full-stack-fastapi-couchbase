# Import installed packages
from apispec import APISpec
from flask_apispec import FlaskApiSpec

# Import app code
from ...main import app
from ...core import config

# Types
from typing import List, Dict

security_definitions = {
    "bearer": {
        "type": "oauth2",
        "flow": "password",
        "tokenUrl": f"{config.API_V1_STR}/login/access-token",
    }
}

app.config.update(
    {
        "APISPEC_SPEC": APISpec(
            title=config.PROJECT_NAME,
            version="v1",
            openapi_version="2.0",
            plugins=("apispec.ext.marshmallow",),
            securityDefinitions=security_definitions,
        ),
        "APISPEC_SWAGGER_URL": f"{config.API_V1_STR}/swagger/",
    }
)
docs = FlaskApiSpec(app)

security_params: List[Dict[str, List]] = [{"bearer": []}]
