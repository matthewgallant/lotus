from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func

from app.extensions import db
from app.models.card import Card
from app.models.card_details import CardDetails

home_bp = Blueprint('home', __name__, template_folder="templates")

@home_bp.route('/')
@login_required
def home():
    # Get total cards in collection
    query = db.select(func.sum(Card.quantity)).where(Card.user_id == current_user.id)
    collection_total = db.session.execute(query).scalar_one_or_none()
    
    # Get total unique card names in collection
    subquery = db.select(func.min(CardDetails.id)).join(Card.details).where(Card.user_id == current_user.id).group_by(CardDetails.name)
    query = db.select(func.count()).select_from(subquery)
    unique_total = db.session.execute(query).scalar_one_or_none()

    return render_template("home.html", collection_total=collection_total, unique_total=unique_total)
