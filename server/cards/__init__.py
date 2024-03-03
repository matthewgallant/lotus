from flask import Blueprint
bp = Blueprint('cards', __name__)
from server.cards import routes
