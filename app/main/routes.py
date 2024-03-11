from flask import render_template
from flask_login import login_required
from sqlalchemy import func

from app.main import bp
from app.extensions import db

from app.models.card import Card

@bp.route('/')
@login_required
def index():
    collection_total = db.session.query(func.sum(Card.quantity)).scalar()
    
    unique_named_cards = db.select(func.min(Card.id)).group_by(Card.name).subquery()
    unique_named_ids = db.select(Card.id).where(Card.id.in_(unique_named_cards))
    unique_total = db.session.execute(db.select(func.count()).select_from(unique_named_ids)).scalar()

    return render_template("index.html", collection_total=collection_total, unique_total=unique_total)
