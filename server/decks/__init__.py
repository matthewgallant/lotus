from flask import Blueprint
bp = Blueprint('decks', __name__)
from server.decks import routes
