from flask import Blueprint
bp = Blueprint('main', __name__)
from server.main import routes
