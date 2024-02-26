from flask import Blueprint
bp = Blueprint('decks', __name__)
from app.decks import routes
