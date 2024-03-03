from server.main import bp
from server.extensions import db

# Load models
from server.models.card import Card

@bp.route('/home')
def index():
    collection_total = db.session.query(Card).count()
    return {
        "total": collection_total
    }
