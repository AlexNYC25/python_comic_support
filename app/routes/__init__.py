from flask import Blueprint

# Define the main blueprint
main_blueprint = Blueprint('main', __name__)

# Import the routes from api.py and register them with the blueprint
from .api import register_routes
register_routes(main_blueprint)
