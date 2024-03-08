from flask import render_template, redirect, request, url_for
from app.decks import bp
from app.extensions import db

# Load models
from app.models.deck_card import DeckCard
from app.models.deck import Deck

@bp.route("/")
def decks():
    decks = db.session.execute(db.select(Deck).order_by(Deck.id.desc())).scalars().all()
    
    # Get color identity
    for deck in decks:
        color_identity = []
        for assoc in deck.mainboard:
            if assoc.card.color_identity:
                colors = assoc.card.color_identity.split(',')
                for color in colors:
                    if color not in color_identity:
                        color_identity.append(color)
        deck.color_identity = color_identity
    
    return render_template("decks/decks.html", decks=decks)
        
@bp.route('/<id>', methods=['GET', 'POST'])
def deck(id):
    deck = db.get_or_404(Deck, id)

    if request.method == 'GET':
        warning = None
        card_names = []
        duplicates = []

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

            # Check for duplicated
            if card.name not in card_names:
                card_names.append(card.name)
            else:
                duplicates.append(card.name)
            
            if len(duplicates) > 0:
                warning = f"There might be duplicates of the following: {', '.join(duplicates)}."

            # Sort cards for gathering
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
            
        return render_template("decks/deck.html", deck=deck, binders=binders, warning=warning)
    else:
        if request.form.get('plains'):
            deck.plains = int(request.form.get('plains'))
        if request.form.get('island'):
            deck.island = int(request.form.get('island'))
        if request.form.get('swamp'):
            deck.swamp = int(request.form.get('swamp'))
        if request.form.get('mountain'):
            deck.mountain = int(request.form.get('mountain'))
        if request.form.get('forest'):
            deck.forest = int(request.form.get('forest'))
        
        db.session.commit()
        return redirect(url_for('decks.deck', id=deck.id, message='Basic lands have been updated for this deck.'))

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
            return render_template("decks/add-deck.html", error='A deck name is required!.')

@bp.route('/<id>/rename', methods=['POST'])
def rename_deck(id):
    deck = db.get_or_404(Deck, id)
    
    if request.form.get("name"):
        deck.name = request.form.get("name")
        db.session.commit()
    
    return redirect(url_for('decks.deck', id=deck.id, message='Deck name has been updated.'))

@bp.route('/<deck_id>/delete')
def delete_deck(deck_id):
    # Delete card associations
    db.session.execute(db.delete(DeckCard).where(DeckCard.deck_id == deck_id))

    # Delete deck
    deck = db.get_or_404(Deck, deck_id)
    db.session.delete(deck)
    db.session.commit()
    
    return redirect(url_for('decks.decks', message=f"{deck.name} has been deleted."))
