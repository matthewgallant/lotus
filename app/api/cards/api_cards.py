from flask import Blueprint, request, abort
from flask_login import login_required, current_user
from markupsafe import escape

from app.extensions import db
from app.models.deck_card import DeckCard
from app.models.card import Card
from app.models.card_details import CardDetails
from app.models.message_log import MessageLog

api_cards_bp = Blueprint('api_cards', __name__)

@api_cards_bp.route('/autocomplete', methods=['POST'])
@login_required
def autocomplete():
    if request.form.get("query"):
        # Get autocomplete results of cards owned by user
        query = db.select(CardDetails.name).join(Card.details).where(CardDetails.name.like(f'%{request.form.get("query")}%'))
        query = query.where(Card.user_id == current_user.id).group_by(CardDetails.name)
        cards = db.session.execute(query).scalars().all()
        
        return cards

@api_cards_bp.route('/<card_id>/quantity', methods=['POST'])
@login_required
def edit_card_quantity(card_id):
    if request.form.get('quantity'):
        card = db.get_or_404(Card, card_id)

        # Unauthorized user
        if card.user_id != current_user.id:
            abort(401)
        
        quantity = int(request.form.get('quantity'))
        card.quantity = quantity

        # Add message log entry
        message = MessageLog(f"Quantity for '{card}' has been changed to {card.quantity}.")
        db.session.add(message)
        db.session.commit()
        
        return { "success": f"The quantity for {card.details.name} ({card.details.set_id}, {card.details.collector_number}) has been changed to {escape(quantity)}. Reload to see changes." }
    else:
        return { "error": "A quantity if required to update." }

@api_cards_bp.route('/delete', methods=['POST'])
@login_required
def delete_card():
    if request.form.get("card_id"):
        card_id = request.form.get("card_id")
        card = db.get_or_404(Card, card_id)

        # Unauthorized user
        if card.user_id != current_user.id:
            abort(401)

        # Delete card associations
        db.session.execute(db.delete(DeckCard).where(DeckCard.card_id == card_id))

        # Need to create string before committing
        return_string = f"{card.details.name} ({card.details.set_id}, {card.details.collector_number}) has been deleted. Reload to see changes."

        # Add message log entry
        message = MessageLog(f"Card '{card}' has been deleted.")
        db.session.add(message)

        # Delete card
        db.session.delete(card)
        db.session.commit()
        
        return { "success": return_string }
    else:
        return { "error": "An error occured while deleting the card." }
