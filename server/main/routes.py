from flask import render_template
from server.main import bp
from server.extensions import db

# Load models
from server.models.card import Card

@bp.route('/')
def index():
    collection_total = db.session.query(Card).count()
    return render_template("index.html", collection_total=collection_total)
