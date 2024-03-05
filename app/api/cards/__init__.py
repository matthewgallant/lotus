from flask import Blueprint
bp = Blueprint('api_cards', __name__)
from app.api.cards import routes
