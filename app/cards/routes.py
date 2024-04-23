import re
import json
import time
import requests
import pprint

from flask import render_template, redirect, request, url_for, abort
from flask_login import login_required, current_user
from sqlalchemy import and_

from app.cards import bp
from app.extensions import db

from app.models.deck import Deck
from app.models.card import Card
from app.models.deck_card import DeckCard
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
    success = None
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
        success = f"{existing_card.details.name}'s quantity has been increased."

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

            success = f"{new_card.details.name} has been added to your collection."

    db.session.commit()
    
    return redirect(url_for('cards.add_card', success=success, error=error))

@bp.route("/import", methods=['GET', 'POST'])
@login_required
def import_cards():
    if request.method == 'GET':
        return render_template("cards/import.html")
    else:
        success = None
        error = None

        if request.form.get('cards'):
            cards_list = request.form.get('cards').split('\n')
            parsed_cards = []
            payload = []
            details = []
            cards = []

            # Generate data for Scryfall query
            for card in cards_list:
                # Ignore blank lines
                if card.strip() == "":
                    break

                # Parse out useful data
                quantity = re.findall(r'^\d+', card)
                set = re.findall(r'\((.*?)\)', card)
                collector_number = re.findall(r'\d+(?![\d\D]*\d)', card)
                foil = re.findall(r'\*F\*', card)

                # Basic validation
                if len(quantity) == 0 or len(set) == 0 or len(collector_number) == 0:
                    error = "Unable to parse cards. No cards have been imported."
                    break

                # Data to be used later in the import
                parsed_cards.append({
                    "set": set[0],
                    "collector_number": collector_number[0],
                    "quantity": int(quantity[0]),
                    "foil": "foil" if len(foil) != 0 else "regular"
                })

                # Data to be sent to Scryfall
                payload.append({
                    "set": set[0],
                    "collector_number": collector_number[0]
                })
            
            # Chunk cards for Scryfall and process chunks
            chunked_payload = [payload[i:i + 75] for i in range(0, len(payload), 75)]
            for chunk in chunked_payload:
                
                # Post chunk to Scryfall
                res = requests.post("https://api.scryfall.com/cards/collection", json={ "identifiers": chunk })
                if res.status_code == 200:

                    # Attempt to read data
                    data = json.loads(res.text)

                    # Handle an incorrect amount of cards returned
                    if len(data['data']) != len(chunk):
                        error = "Unable to fetch cards from Scryfall. No cards have been imported."
                        break

                    for card in data['data']:
                        # Attempt to find existing card details
                        detail = db.session.execute(db.select(CardDetails).where(CardDetails.scryfall_id == card['id'])).scalar_one_or_none()

                        # Create details if needed
                        if detail:
                            details.append(detail)
                        else:
                            # Store variables for later
                            scryfall_id = name = set_id = collector_number = color_identity = type_line = cmc = None
                            power = toughness = rarity = text = price_regular = price_foil = price_etched = None

                            # Parse Scryfall data
                            if 'id' in card:
                                scryfall_id = card['id']
                            if 'name' in card:
                                name = card['name']
                            if 'set' in card:
                                set_id = card['set'].upper()
                            if 'collector_number' in card:
                                collector_number = card['collector_number']
                            if 'color_identity' in card:
                                if card['color_identity']:
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
                            if 'prices' in card:
                                if 'usd' in card['prices']:
                                    price_regular = card['prices']['usd']
                                if 'usd_foil' in card['prices']:
                                    price_foil = card['prices']['usd_foil']
                                if 'usd_etched' in card['prices']:
                                    price_etched = card['prices']['usd_etched']
                            
                            # Don't import basic lands
                            if name.lower() not in ("plains", "island", "swamp", "mountain", "forest"):
                                detail = CardDetails(name, set_id, collector_number, color_identity, scryfall_id, type_line,
                                                            cmc, power, toughness, rarity, text, price_regular, price_foil, price_etched)
                                details.append(detail)
                                db.session.add(detail)
                                db.session.flush()

                                # Add message log entry
                                message = MessageLog(f"New card details '{detail}' has been added via import.")
                                db.session.add(message)
                else:
                    error = "Unable to reach Scryfall. No cards have been imported."
                    break

                # Break entire import if a parsed card can't be matched
                if error:
                    break
            
                # Sleep before continuing to be polite
                time.sleep(0.1)
            
            # Add new user cards using foil data
            if not error:
                for detail in details:
                    # Find parsed card for foil info
                    matched_parsed_cards = list(filter(lambda c: c['set'] == detail.set_id and c['collector_number'] == detail.collector_number, parsed_cards))

                    # Basic data validation
                    if len(matched_parsed_cards) != 1:
                        error = "Unable to match cards. No cards have been imported."
                        break

                    # Attempt to find existing user card
                    matched_parsed_card = matched_parsed_cards[0]
                    card = db.session.execute(db.select(Card).where(and_(Card.card_details_id == detail.id, Card.foil == matched_parsed_card["foil"]))).scalar_one_or_none()

                    if card:
                        # Increase quantity if already exists
                        print(card.quantity)
                        print(matched_parsed_card)
                        card.quantity += matched_parsed_card["quantity"]
                    else:
                        # Create new user card in db if it doesn't already exist
                        card = Card(current_user.id, detail.id, matched_parsed_card["quantity"], matched_parsed_card["foil"])

                    # Store card away
                    cards.append(card)
                    db.session.add(card)
                    db.session.flush()

                    # Add message log entry
                    message = MessageLog(f"New card '{card}' has been added via import.")
                    db.session.add(message)
            
            # Create new deck if requested and add cards to it
            if request.form.get("deck") and not error:
                deck = Deck(current_user.id, request.form.get("deck"))
                db.session.add(deck)
                db.session.flush()

                # Add message log entry
                message = MessageLog(f"New deck '{deck}' has been added via import.")
                db.session.add(message)

                # Link imported cards to new deck
                for card in cards:
                    deck_card = DeckCard(deck.id, card.id, 'm')
                    deck.mainboard.append(deck_card)

                    # Add message log entry
                    message = MessageLog(f"Card '{card}' has been added to deck '{deck}' via import.")
                    db.session.add(message)

            # Commit to database if no errors
            if not error:
                db.session.commit()
                success = "Cards have been imported successfully!"
        else:
            error = "A list of cards must be provided for importing!"
            
        return redirect(url_for('cards.import_cards', success=success, error=error))
