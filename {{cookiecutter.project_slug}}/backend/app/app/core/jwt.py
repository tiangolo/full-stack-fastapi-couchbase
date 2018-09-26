# Import standard library modules

# Import installed modules
from flask_jwt_extended import JWTManager

# Import app code
from ..main import app
from app.db.utils import get_user

# Setup the Flask-JWT-Extended extension
jwt = JWTManager(app)


@jwt.user_loader_callback_loader
def get_current_user(identity):
    return get_user(identity)
