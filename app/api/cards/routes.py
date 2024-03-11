from flask import request
from flask_login import login_required

from app.api.cards import bp
from app.extensions import db

from app.models.deck_card import DeckCard
from app.models.card import Card

@bp.route('/autocomplete', methods=['POST'])
@login_required
def autocomplete():
    if request.form.get("query"):
        cards = db.session.execute(
            db.select(Card.name)
                .where(Card.name.like(f'%{request.form.get("query")}%'))
                .group_by(Card.name)
            ).scalars().all()
        return cards

@bp.route('/<card_id>/quantity', methods=['POST'])
@login_required
def edit_card_quantity(card_id):
    if request.form.get('quantity'):
        card = db.get_or_404(Card, card_id)
        
        card.quantity = request.form.get('quantity')
        db.session.commit()
        
        return { "success": f"The for {card.name} ({card.set_id}, {card.collector_number}) quantity has been changed to {request.form.get('quantity')}. Reload to see changes." }
    else:
        return { "error": "A quantity if required to update." }

@bp.route('/delete', methods=['POST'])
@login_required
def delete_card():
    if request.form.get("card_id"):
        card_id = request.form.get("card_id")

        # Get the card or 404
        card = db.get_or_404(Card, card_id)

        # Delete card associations
        db.session.execute(db.delete(DeckCard).where(DeckCard.card_id == card_id))

        # Delete card
        db.session.delete(card)
        db.session.commit()
        
        return { "success": f"{card.name} ({card.set_id}, {card.collector_number}) has been deleted. Reload to see changes." }
    else:
        return { "error": "An error occured while deleting the card." }
