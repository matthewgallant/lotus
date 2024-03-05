from flask import Blueprint
bp = Blueprint('api_decks', __name__)
from app.api.decks import routes
