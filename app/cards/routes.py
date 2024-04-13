import json
import requests

from flask import render_template, redirect, request, url_for, abort
from flask_login import login_required, current_user
from sqlalchemy import and_

from app.cards import bp
from app.extensions import db

from app.models.deck import Deck
from app.models.card import Card
from app.models.card_details import CardDetails
from app.models.message_log import MessageLog

@bp.route("/")
def cards():
    # Get cards owned by user
    query = db.select(Card).join(Card.details).order_by(
        db.case(
            (and_(Card.foil == "regular", CardDetails.price_regular), CardDetails.price_regular),
            (and_(Card.foil == "foil", CardDetails.price_foil), CardDetails.price_foil),
            (and_(Card.foil == "foil", CardDetails.price_etched), CardDetails.price_etched),
            (CardDetails.price_regular, CardDetails.price_regular),
            (CardDetails.price_foil, CardDetails.price_foil),
            (CardDetails.price_etched, CardDetails.price_etched)
        ).desc()
    )
    cards = db.paginate(query, per_page=50)

    # Get decks owned by user
    query = db.select(Deck).where(Deck.user_id == current_user.id).order_by(Deck.id.desc())
    decks = db.session.execute(query).scalars().all()
    
    return render_template("cards/cards.html", cards=cards, decks=decks)

@bp.route("/<id>")
@login_required
def card(id):
    card = db.get_or_404(Card, id)

    # Unauthorized user
    if card.user_id != current_user.id:
        abort(401)
    
    # Get cards owned by user
    query = db.select(Card).join(Card.details).where(CardDetails.name == card.details.name).where(Card.user_id == current_user.id)
    cards = db.session.execute(query).scalars().all()

    # Get decks owned by user
    query = db.select(Deck).where(Deck.user_id == current_user.id).order_by(Deck.id.desc())
    decks = db.session.execute(query).scalars().all()

    return render_template("cards/card.html", card=card, cards=cards, decks=decks)
    
@bp.route('/<card_id>/decks')
@login_required
def card_decks(card_id):
    card = db.get_or_404(Card, card_id)

    # Unauthorized user
    if card.user_id != current_user.id:
        abort(401)

    return render_template("cards/card-decks.html", card=card)

@bp.route("/add")
@login_required
def add_card():
    return render_template("cards/add-card.html")
    
@bp.route("/add/<scryfall_id>")
@login_required
def add_card_from_scryfall(scryfall_id):
    message = None
    error = None

    # Handle foils
    foil = 'regular'
    if request.args.get('foil'):
        foil = 'foil'
    
    # Find existing card owned by user
    query = db.select(Card).join(Card.details).where(CardDetails.scryfall_id == scryfall_id)
    query = query.where(Card.foil == foil).where(Card.user_id == current_user.id)
    existing_card = db.session.execute(query).scalar()

    if existing_card:
        existing_card.quantity += 1
        message = f"{existing_card.name}'s quantity has been increased."

        # Add message log entry
        message = MessageLog(f"Quantity for '{existing_card}' has been increased.")
        db.session.add(message)
    else:
        # Find if we have the card details already
        query = db.select(CardDetails).where(CardDetails.scryfall_id == scryfall_id)
        existing_details = db.session.execute(query).scalar_one_or_none()
        details_id = None

        if existing_details:
            details_id = existing_details.id
        else:
            res = requests.get(f'https://api.scryfall.com/cards/{scryfall_id}')
            if res.status_code == 200:
                data = json.loads(res.text)

                name = None
                set_id = None
                collector_number = None
                color_identity = None
                type_line = None
                cmc = None
                power = None
                toughness = None
                rarity = None
                text = None
                price_regular = None
                price_foil = None
                price_etched = None

                if 'name' in data:
                    name = data['name']
                if 'set' in data:
                    set_id = data['set'].upper()
                if 'collector_number' in data:
                    collector_number = data['collector_number']
                if 'color_identity' in data:
                    if data['color_identity']:
                        color_identity = ",".join(data['color_identity'])
                if 'type_line' in data:
                    type_line = data['type_line']
                if 'cmc' in data:
                    cmc = data['cmc']
                if 'power' in data:
                    power = data['power']
                if 'toughness' in data:
                    toughness = data['toughness']
                if 'rarity' in data:
                    rarity = data['rarity']
                if 'oracle_text' in data:
                    text = data['oracle_text']
                if 'prices' in data:
                    if 'usd' in data['prices']:
                        price_regular = data['prices']['usd']
                    if 'usd_foil' in data['prices']:
                        price_foil = data['prices']['usd_foil']
                    if 'usd_etched' in data['prices']:
                        price_etched = data['prices']['usd_etched']
                
                new_details = CardDetails(
                    name,
                    set_id,
                    collector_number,
                    color_identity,
                    scryfall_id,
                    type_line,
                    cmc,
                    power,
                    toughness,
                    rarity,
                    text,
                    price_regular,
                    price_foil,
                    price_etched
                )
                db.session.add(new_details)
                db.session.flush()

                # Add message log entry
                message = MessageLog(f"New card details '{new_details}' has been added.")
                db.session.add(message)

                details_id = new_details.id
            else:
                error = "An error has occured when trying to add the card."
    
    # Create card if card details exist
    if details_id:
        new_card = Card(
            current_user.id,
            details_id,
            1, # Quantity
            foil
        )
        db.session.add(new_card)
        db.session.flush()

        # Add message log entry
        message = MessageLog(f"New card '{new_card}' has been added.")
        db.session.add(message)

        message = f"{new_card.details.name} has been added to your collection."

    db.session.commit()
    
    return redirect(url_for('cards.add_card', message=message, error=error))

@bp.route("/import", methods=['GET', 'POST'])
@login_required
def import_cards():
    if request.method == 'GET':
        return render_template("cards/import.html")
    else:
        message = None
        error = None
        errors = []

        if request.form.get('cardList'):
            cardList = request.form.get('cardList')
            for line in cardList.split('\n'):
                if len(line.strip()) > 0:
                    quantity = None
                    name = None
                    variant = None
                    set = None
                    foil = "regular"

                    # Handle card type
                    if request.form.get("cardsType"):
                        if request.form.get("cardsType") == "foil":
                            foil = "foil"

                    # Collect quantity and set since they're always first and last
                    line_parts = line.split(" ")
                    quantity = line_parts.pop(0)
                    set = line_parts.pop().replace('[', '').replace(']', '')

                    # Collect optional varient if it's the last item
                    if "<" in line_parts[-1]:
                        variant = line_parts.pop().replace('<', '').replace('>', '')
                    
                    # The rest of the words should be the name
                    name = " ".join(line_parts)
                    
                    if name.lower() not in ("plains", "island", "swamp", "mountain", "forest"):
                        # Obtain Scryfall card
                        if variant:
                            res = requests.get(f"https://api.scryfall.com/cards/search?q={name}+game:paper+set:{set}+is:{variant}")
                        else:
                            res = requests.get(f"https://api.scryfall.com/cards/search?q={name}+game:paper+set:{set}")
                        data = res.json()
                        
                        if res.status_code == 200:
                            if 'data' in data:
                                if len(data['data']) > 0:
                                    card = data['data'][0]

                                    scryfall_id = None
                                    name = None
                                    set_id = None
                                    collector_number = None
                                    color_identity = None
                                    type_line = None
                                    cmc = None
                                    power = None
                                    toughness = None
                                    rarity = None
                                    text = None
                                    price_regular = None
                                    price_foil = None
                                    price_etched = None

                                    if 'id' in card:
                                        scryfall_id = card['id']
                                    if 'name' in card:
                                        name = card['name']
                                    if 'set' in card:
                                        set_id = card['set'].upper()
                                    if 'collector_number' in card:
                                        collector_number = card['collector_number']
                                    if 'color_identity' in card:
                                        if card['color_identity'] != []:
                                            color_identity = ",".join(card['color_identity'])
                                    if 'type_line' in card:
                                        type_line = card['type_line']
                                    if 'cmc' in card:
                                        cmc = card['cmc']
                                    if 'power' in card:
                                        power = card['power']
                                    if 'toughness' in card:
                                        toughness = card['toughness']
                                    if 'rarity' in card:
                                        rarity = card['rarity']
                                    if 'oracle_text' in card:
                                        text = card['oracle_text']
                                    if 'prices' in data:
                                        if 'usd' in data['prices']:
                                            price_regular = data['prices']['usd']
                                        if 'usd_foil' in data['prices']:
                                            price_foil = data['prices']['usd_foil']
                                        if 'usd_etched' in data['prices']:
                                            price_etched = data['prices']['usd_etched']
                                    
                                    query = db.select(CardDetails).where(CardDetails.scryfall_id == scryfall_id)
                                    existing_details = db.session.execute(query).scalar_one_or_none()
                                    details_id = None

                                    if existing_details:
                                        details_id = existing_details.id
                                    else:
                                        new_details = CardDetails(
                                            name,
                                            set_id,
                                            collector_number,
                                            color_identity,
                                            scryfall_id,
                                            type_line,
                                            cmc,
                                            power,
                                            toughness,
                                            rarity,
                                            text,
                                            price_regular,
                                            price_foil,
                                            price_etched
                                        )
                                        db.session.add(new_details)
                                        db.session.flush()

                                        # Add message log entry
                                        message = MessageLog(f"New card details '{new_details}' has been added.")
                                        db.session.add(message)

                                        details_id = new_details.id

                                    if details_id:
                                        new_card = Card(
                                            current_user.id,
                                            details_id,
                                            quantity,
                                            foil
                                        )
                                        db.session.add(new_card)
                                        db.session.flush()

                                        # Add message log entry
                                        message = MessageLog(f"New card '{new_card}' has been added.")
                                        db.session.add(message)
                                else:
                                    error = True
                                    errors.append(line)
                            else:
                                error = True
                                errors.append(line)
                        else:
                            error = True
                            errors.append(line)
        else:
            error = "A card list is required to import."

        if not error:
            db.session.commit()
            message = "Successfully imported all cards to collection."
        elif error == True:
            error = "Unable to retrive the following cards from Scryfall. No cards have been imported."
        
        if len(errors) == 0:
            errors = None
        else:
            errors = "|".join(errors)
            
        return redirect(url_for('cards.import_cards', message=message, error=error, errors=errors))
