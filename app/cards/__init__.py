from flask import Blueprint
bp = Blueprint('cards', __name__)
from app.cards import routes
