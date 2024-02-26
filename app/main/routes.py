from flask import render_template
from app.main import bp
from app.extensions import db

# Load models
from app.models.card import Card

@bp.route('/')
def index():
    collection_total = db.session.query(Card).count()
    return render_template("index.html", collection_total=collection_total)
