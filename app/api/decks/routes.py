from flask import request, abort
from flask_login import login_required, current_user

from app.api.decks import bp
from app.extensions import db

from app.models.deck_card import DeckCard
from app.models.deck import Deck
from app.models.card import Card

@bp.route('/<deck_id>/add', methods=['POST'])
@login_required
def add_card_to_deck(deck_id):
    if request.form.get("card_id") and request.form.get("board"):
        card_id = request.form.get("card_id")
        board = request.form.get("board")

        deck = db.get_or_404(Deck, deck_id)
        card = db.get_or_404(Card, card_id)

        # Unauthorized user
        if card.user_id != current_user.id or deck.user_id != current_user.id:
            abort(401)

        # Create new deck/card link
        deck_card = DeckCard(deck.id, card.id, board)
        if board == 'm':
            deck.mainboard.append(deck_card)
        elif board == 's':
            deck.sideboard.append(deck_card)
        
        db.session.commit()
        
        return { "success": f"{card.name} has been added to {deck.name}." }
    else:
        return { "error": "An error occured while trying to add the card to the deck." }

@bp.route('/card/move', methods=['POST'])
@login_required
def move_card_board():
    if request.form.get("assoc_id") and request.form.get("board"):
        assoc_id = request.form.get("assoc_id")
        board = request.form.get("board")

        # Get association
        query = db.select(DeckCard).where(DeckCard.id == assoc_id)
        assoc = db.session.execute(query).scalar()

        # Unauthorized user
        if assoc.deck.user_id != current_user.id:
            abort(401)

        # Change and commit board
        assoc.board = board
        db.session.commit()
        
        return { "success": f"{assoc.card.name} has been moved to the {'mainboard' if board == 'm' else 'sideboard'}. Reload to see changes." }
    else:
        return { "error": "An error occured while moving the card's board." }
    
@bp.route('/card/commander', methods=['POST'])
@login_required
def set_commander_for_deck():
    if request.form.get("assoc_id") and request.form.get("set_commander"):
        assoc_id = request.form.get("assoc_id")
        set_commander = request.form.get("set_commander")

        # Get association
        query = db.select(DeckCard).where(DeckCard.id == assoc_id)
        assoc = db.session.execute(query).scalar()

        # Unauthorized user
        if assoc.deck.user_id != current_user.id:
            abort(401)
        
        # Toggle commander status
        if (set_commander == "set"):
            assoc.is_commander = True
        else:
            assoc.is_commander = False
        
        db.session.commit()
        
        return { "success": f"{assoc.card.name} has been {set_commander} as commander. Reload to see changes." }
    else:
        return { "error": "An error occured while trying to change the commander status." }

@bp.route('/card/remove', methods=['POST'])
@login_required
def remove_card_from_deck():
    if request.form.get("assoc_id"):
        assoc_id = request.form.get("assoc_id")

        # Get association
        query = db.select(DeckCard).where(DeckCard.id == assoc_id)
        assoc = db.session.execute(query).scalar()

        # Unauthorized user
        if assoc.deck.user_id != current_user.id:
            abort(401)
        
        # Delete association
        query = db.delete(DeckCard).where(DeckCard.id == assoc_id)
        db.session.execute(query)

        # Need to create string before committing
        return_string = { "success": f"{assoc.card.name} has been removed from {assoc.deck.name}." }
        
        db.session.commit()

        return return_string
    else:
        return { "error": "An error occured when trying to remove card from deck." }
    
