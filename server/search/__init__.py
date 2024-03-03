from flask import Blueprint
bp = Blueprint('search', __name__)
from server.search import routes
