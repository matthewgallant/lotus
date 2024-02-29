from flask import render_template, redirect, request, url_for
from app.decks import bp
from app.extensions import db

# Load models
from app.models.deck_card import DeckCard
from app.models.deck import Deck
from app.models.card import Card

@bp.route("/")
def decks():
    decks = db.session.execute(db.select(Deck).order_by(Deck.id.desc())).scalars().all()
    return render_template("decks/decks.html", decks=decks)

@bp.route("/add", methods=['GET', 'POST'])
def add_deck():
    if request.method == 'GET':
        return render_template("decks/add-deck.html")
    else:
        if request.form.get('name'):
            deck = Deck(name=request.form.get('name'))
            db.session.add(deck)
            db.session.commit()
            return redirect(url_for('decks.deck', id=deck.id))
        else:
            return render_template("decks/add-deck.html", error='A deck name is required!')
        
@bp.route('/<id>', methods=['GET', 'POST'])
def deck(id):
    deck = db.get_or_404(Deck, id)
    if request.method == 'GET':
        return render_template("decks/deck.html", deck=deck)
    else:
        deck.plains = request.form.get('plains')
        deck.island = request.form.get('island')
        deck.swamp = request.form.get('swamp')
        deck.mountain = request.form.get('mountain')
        deck.forest = request.form.get('forest')
        db.session.commit()
        return redirect(url_for('decks.deck', id=deck.id, message='Basic lands have been updated for this deck'))
    
@bp.route('/<id>/gather')
def gather_deck(id):
    deck = db.get_or_404(Deck, id)
    binders = {
        "legendary": {
            "mythic": [],
            "rare": [],
            "uncommon": [],
            "common": []
        },
        "white": {
            "mythic": [],
            "rare": [],
            "uncommon": [],
            "common": []
        },
        "blue": {
            "mythic": [],
            "rare": [],
            "uncommon": [],
            "common": []
        },
        "black": {
            "mythic": [],
            "rare": [],
            "uncommon": [],
            "common": []
        },
        "red": {
            "mythic": [],
            "rare": [],
            "uncommon": [],
            "common": []
        },
        "green": {
            "mythic": [],
            "rare": [],
            "uncommon": [],
            "common": []
        },
        "multi": {
            "mythic": [],
            "rare": [],
            "uncommon": [],
            "common": []
        },
        "colorless": {
            "mythic": [],
            "rare": [],
            "uncommon": [],
            "common": []
        },
        "lands": {
            "mythic": [],
            "rare": [],
            "uncommon": [],
            "common": []
        }
    }

    for assoc in deck.mainboard:
        card = assoc.card

        if "legendary creature" in card.type_line.lower() or (card.text is not None and "be your commander" in card.text): # Commanders
            binders["legendary"][card.rarity].append(card)
        elif "land" in card.type_line.lower(): # Lands
            binders["lands"][card.rarity].append(card)
        elif card.color_identity == None: # Colorless
            binders["colorless"][card.rarity].append(card)
        elif card.color_identity == 'W': # White
            binders["white"][card.rarity].append(card)
        elif card.color_identity == 'U': # Blue
            binders["blue"][card.rarity].append(card)
        elif card.color_identity == 'B': # Black
            binders["black"][card.rarity].append(card)
        elif card.color_identity == 'R': # Red
            binders["red"][card.rarity].append(card)
        elif card.color_identity == 'G': # Green
            binders["green"][card.rarity].append(card)
        elif len(card.color_identity) > 1: # Multi
            binders["multi"][card.rarity].append(card)
        
    return render_template("decks/gather.html", deck=deck, binders=binders)

@bp.route('/<deck_id>/card/<card_id>/add/<board>')
def add_card_to_deck(deck_id, card_id, board):
    deck = db.get_or_404(Deck, deck_id)
    card = db.get_or_404(Card, card_id)
    deck_card = DeckCard()
    deck_card.card = card
    deck_card.board = board
    if board == 'm':
        deck.mainboard.append(deck_card)
    elif board == 's':
        deck.sideboard.append(deck_card)
    db.session.commit()
    return redirect(url_for('cards.card', id=card_id, message=f'{card.name} has been added to deck {deck.name}'))

@bp.route('/<deck_id>/card/<card_id>/assoc/<assoc_id>/remove')
def remove_card_from_deck(deck_id, card_id, assoc_id):
    card = db.get_or_404(Card, card_id)
    db.session.execute(db.delete(DeckCard).where(DeckCard.id == assoc_id))
    db.session.commit()
    return redirect(url_for('decks.deck', id=deck_id, message=f'{card.name} has been removed from this deck'))

@bp.route('/<deck_id>/assoc/<assoc_id>/commander/set')
def set_commander_for_deck(deck_id, assoc_id):
    assoc = db.session.execute(db.select(DeckCard).where(DeckCard.id == assoc_id)).scalar()
    assoc.is_commander = True
    db.session.commit()
    return redirect(url_for('decks.deck', id=deck_id, message="A new commander has been set"))

@bp.route('/<deck_id>/assoc/<assoc_id>/commander/unset')
def unset_commander_for_deck(deck_id, assoc_id):
    assoc = db.session.execute(db.select(DeckCard).where(DeckCard.id == assoc_id)).scalar()
    assoc.is_commander = False
    db.session.commit()
    return redirect(url_for('decks.deck', id=deck_id, message="The commander has been unset"))

@bp.route('/<deck_id>/assoc/<assoc_id>/board/<board>')
def move_card_board(deck_id, assoc_id, board):
    assoc = db.session.execute(db.select(DeckCard).where(DeckCard.id == assoc_id)).scalar()
    assoc.board = board
    db.session.commit()
    return redirect(url_for('decks.deck', id=deck_id, message="The card's board has been updated"))

@bp.route('/<deck_id>/delete')
def delete_deck(deck_id):
    # Delete card associations
    db.session.execute(db.delete(DeckCard).where(DeckCard.deck_id == deck_id))

    # Delete deck
    deck = db.get_or_404(Deck, deck_id)
    db.session.delete(deck)
    db.session.commit()
    
    return redirect(url_for('decks.decks', message=f"{deck.name} has been deleted"))
