from flask import render_template, redirect, request, url_for, abort
from flask_login import login_required, current_user

from app.decks import bp
from app.extensions import db

from app.models.deck_card import DeckCard
from app.models.deck import Deck
from app.models.card_details import CardDetails
from app.models.message_log import MessageLog

@bp.route("/")
@login_required
def decks():
    # Get decks owned by user
    query = db.select(Deck).where(Deck.user_id == current_user.id).order_by(Deck.id.desc())
    decks = db.paginate(query, per_page=10)
    
    # Get color identity
    for deck in decks:
        color_identity = []

        # Get only commanders for a quick color identity
        commanders = list(filter(lambda x: x.is_commander, deck.mainboard))
        
        # Gather all colors in all commanders for a given deck (faster)
        if len(commanders) > 0:
            for commander in commanders:
                colors = commander.card.details.color_identity.split(',')
                for color in colors:
                    if color not in color_identity:
                        color_identity.append(color)
        # No commander, get color identity from cards (slower)
        else:
            for card in deck.mainboard:
                if card.card.details.color_identity:
                    colors = card.card.details.color_identity.split(',')
                    for color in colors:
                        if color not in color_identity:
                            color_identity.append(color)

        # Set the color identity
        deck.color_identity = color_identity
    
    return render_template("decks/decks.html", decks=decks)
        
@bp.route('/<id>', methods=['GET', 'POST'])
@login_required
def deck(id):
    deck = db.get_or_404(Deck, id)

    # Unauthorized user
    if deck.user_id != current_user.id:
        abort(401)

    if request.method == 'GET':
        warning = None
        card_names = []
        duplicates = []
        price = 0

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
            if card.details.name not in card_names:
                card_names.append(card.details.name)
            else:
                duplicates.append(card.details.name)
            
            if len(duplicates) > 0:
                warning = f"There are duplicates of the following: {', '.join(duplicates)}."
            
            # Gather price data
            if card.foil == "regular" and card.details.price_regular:
                price += card.details.price_regular
            elif card.foil == "foil" and card.details.price_foil:
                price += card.details.price_foil
            elif card.foil == "foil" and card.details.price_etched:
                price += card.details.price_etched
            elif card.details.price_regular:
                price += card.details.price_regular
            elif card.details.price_foil:
                price += card.details.price_foil
            elif card.details.price_etched:
                price += card.details.price_etched

            # Sort cards for gathering
            if ("legendary" in card.details.type_line.lower() and "creature" in card.details.type_line.lower()) or (card.details.text is not None and "be your commander" in card.details.text): # Commanders
                binders["legendary"][card.details.rarity].append(card)
            elif card.details.type_line.lower() == "land": # Lands
                binders["lands"][card.details.rarity].append(card)
            elif card.details.color_identity == None: # Colorless
                binders["colorless"][card.details.rarity].append(card)
            elif card.details.color_identity == 'W': # White
                binders["white"][card.details.rarity].append(card)
            elif card.details.color_identity == 'U': # Blue
                binders["blue"][card.details.rarity].append(card)
            elif card.details.color_identity == 'B': # Black
                binders["black"][card.details.rarity].append(card)
            elif card.details.color_identity == 'R': # Red
                binders["red"][card.details.rarity].append(card)
            elif card.details.color_identity == 'G': # Green
                binders["green"][card.details.rarity].append(card)
            elif card.details.color_identity: # Multi
                binders["multi"][card.details.rarity].append(card)
            
        return render_template("decks/deck.html", deck=deck, binders=binders, warning=warning, price=price)
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
        
        # Add message log entry
        message = MessageLog(f"Lands for '{deck}' have been updated.")
        db.session.add(message)
        db.session.commit()

        return redirect(url_for('decks.deck', id=deck.id, message='Basic lands have been updated for this deck.'))

@bp.route("/add", methods=['GET', 'POST'])
@login_required
def add_deck():
    if request.method == 'GET':
        return render_template("decks/add-deck.html")
    else:
        if request.form.get('name'):
            deck = Deck(current_user.id, request.form.get('name'))
            db.session.add(deck)
            db.session.commit()

            # Add message log entry
            message = MessageLog(f"New deck '{deck}' has been added.")
            db.session.add(message)
            db.session.commit()
            
            return redirect(url_for('decks.deck', id=deck.id))
        else:
            return render_template("decks/add-deck.html", error='A deck name is required!.')

@bp.route('/<id>/notes', methods=['POST'])
@login_required
def deck_notes(id):
    deck = db.get_or_404(Deck, id)

    # Unauthorized user
    if deck.user_id != current_user.id:
        abort(401)
    
    if request.form.get("notes"):
        deck.notes = request.form.get("notes")

        # Add message log entry
        message = MessageLog(f"Notes for '{deck}' have been updated.")
        db.session.add(message)
        db.session.commit()
    
    return redirect(url_for('decks.deck', id=deck.id, message='Deck notes have been updated.'))

@bp.route('/<id>/rename', methods=['POST'])
@login_required
def rename_deck(id):
    deck = db.get_or_404(Deck, id)

    # Unauthorized user
    if deck.user_id != current_user.id:
        abort(401)
    
    if request.form.get("name"):
        name = request.form.get("name")

        # Add message log entry
        message = MessageLog(f"Name for '{deck}' has been updated to '{name}'.")
        db.session.add(message)

        deck.name = name
        db.session.commit()
    
    return redirect(url_for('decks.deck', id=deck.id, message='Deck name has been updated.'))

@bp.route('/<deck_id>/archive')
@login_required
def archive_deck(deck_id):
    deck = db.get_or_404(Deck, deck_id)
    
    # Unauthorized user
    if deck.user_id != current_user.id:
        abort(401)

    # Change card associations to archived values
    for assoc in deck.mainboard:
        assoc.board = 'am'
    for assoc in deck.sideboard:
        assoc.board = 'as'
    
    # Change deck to archived
    deck.archived = True

    # Add message log entry
    message = MessageLog(f"Deck '{deck}' has been archived.")
    db.session.add(message)
    db.session.commit()
    
    return redirect(url_for('decks.deck', id=deck_id, message=f"{deck.name} has been archived."))

@bp.route('/<deck_id>/unarchive')
@login_required
def unarchive_deck(deck_id):
    deck = db.get_or_404(Deck, deck_id)
    
    # Unauthorized user
    if deck.user_id != current_user.id:
        abort(401)

    # Change card associations to unarchived values
    for assoc in deck.mainboard:
        assoc.board = 'm'
    for assoc in deck.sideboard:
        assoc.board = 's'
    
    # Change deck to unarchived
    deck.archived = False

    # Add message log entry
    message = MessageLog(f"Deck '{deck}' has been unarchived.")
    db.session.add(message)
    db.session.commit()
    
    return redirect(url_for('decks.deck', id=deck_id, message=f"{deck.name} has been unarchived."))

@bp.route('/<deck_id>/delete')
@login_required
def delete_deck(deck_id):
    deck = db.get_or_404(Deck, deck_id)
    
    # Unauthorized user
    if deck.user_id != current_user.id:
        abort(401)

    # Delete card associations
    db.session.execute(db.delete(DeckCard).where(DeckCard.deck_id == deck_id))

    # Add message log entry
    message = MessageLog(f"Deck '{deck}' has been deleted.")
    db.session.add(message)

    # Delete deck
    db.session.delete(deck)
    db.session.commit()
    
    return redirect(url_for('decks.decks', message=f"{deck.name} has been deleted."))
