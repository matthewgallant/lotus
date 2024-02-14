import os
import json
import requests

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class DeckCard(db.Model):
    __tablename__ = "decks_cards"

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    deck_id = db.Column(db.Integer, db.ForeignKey('decks.id'), nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), nullable=False)
    is_commander = db.Column(db.Boolean)

    deck = db.relationship('Deck', back_populates='cards')
    card = db.relationship('Card', back_populates='decks')

class Deck(db.Model):
    __tablename__ = "decks"

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    plains = db.Column(db.Integer)
    island = db.Column(db.Integer)
    swamp = db.Column(db.Integer)
    mountain = db.Column(db.Integer)
    forest = db.Column(db.Integer)

    cards = db.relationship('DeckCard', back_populates='deck', order_by='DeckCard.is_commander.desc()')

class Card(db.Model):
    __tablename__ = "cards"

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    set_id = db.Column(db.String)
    quantity = db.Column(db.Integer)
    foil = db.Column(db.String)
    collector_number = db.Column(db.Integer)
    scryfall_id = db.Column(db.String, nullable=False)
    color_identity = db.Column(db.String)
    type_line = db.Column(db.String)
    cmc = db.Column(db.Integer)
    power = db.Column(db.Integer)
    toughness = db.Column(db.Integer)
    rarity = db.Column(db.String)
    text = db.Column(db.String)

    decks = db.relationship('DeckCard', back_populates='card')

# Create the app
app = Flask(__name__)

# Load database path from .env
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']

# Initialize the app with the database
db.init_app(app)

def handle_search():
    query = db.select(Card).group_by(Card.name)

    if request.args.get('name'):
        query = query.where(Card.name.like(f'%{request.args.get("name")}%'))
    if request.args.get('text'):
        query = query.where(Card.text.like(f'%{request.args.get("text")}%'))
    if request.args.get('type'):
        query = query.where(Card.type_line.like(f'%{request.args.get("type")}%'))
    if request.args.get('set'):
        query = query.where(Card.set_id == request.args.get('set'))
    if request.args.get('rarity'):
        query = query.where(Card.rarity == request.args.get('rarity'))
    if request.args.get('color'):
        colors = request.args.get('color').split(',')
        core_colors = ['w', 'u', 'b', 'r', 'g']
        if 'un' in colors:
            query = query.where(Card.color_identity == None, Card.type_line.notlike('land'))
        else:
            for color in core_colors:
                if color in colors:
                    query = query.where(Card.color_identity.contains(color))
                else:
                    query = query.where(Card.color_identity.notlike(f'%{color}%'))
    
    return db.paginate(query, per_page=12)

@app.route("/")
def home():
    collection_total = db.session.query(Card).count()
    return render_template("home.html", collection_total=collection_total)

@app.route("/search")
def search():
    sets = db.session.execute(db.select(Card.set_id).group_by(Card.set_id))
    return render_template("search.html", sets=sets)

@app.route("/results", methods=['GET', 'POST'])
def results():
    if request.method == 'POST':
        params = {}

        # Process POST data
        if request.form.get('name'):
            params['name'] = request.form.get('name').strip().lower()
        if request.form.get('text'):
            params['text'] = request.form.get('text').strip().lower()
        if request.form.get('type'):
            params['type'] = request.form.get('type').strip().lower()
        if request.form.get('set'):
            params['set'] = request.form.get('set').strip().upper()
        if request.form.get('rarity'):
            params['rarity'] = request.form.get('rarity')
        if len(request.form.getlist('color')) > 0:
            params['color'] = ",".join(request.form.getlist("color"))
        
        # Redirect to GET url
        return redirect(url_for('results', **params))
    else:
        cards = handle_search()

        # Redirect to card page if only 1 card is found
        if cards.total == 1:
            return redirect(url_for('card', id=cards.items[0].id))
        else:
            return render_template("results.html", cards=cards)

@app.route("/api/cards")
def api_cards():
    cards = handle_search()
    return render_template("api/cards.html", cards=cards)

@app.route("/card/<id>")
def card(id):
    card = db.get_or_404(Card, id)
    cards = db.session.execute(db.select(Card).where(Card.name == card.name)).scalars().all()
    decks = db.session.execute(db.select(Deck).order_by(Deck.id.desc())).scalars().all()
    return render_template("card.html", card=card, cards=cards, decks=decks)

@app.route("/card/add")
def add_card():
    return render_template("add-card.html")
    
@app.route("/card/add/<scryfall_id>")
def add_card_from_scryfall(scryfall_id):
    message = None
    error = None

    # Handle foils
    foil = 'regular'
    if request.args.get('foil'):
        foil = 'foil'
    
    existing_card = db.session.execute(db.select(Card).where(Card.scryfall_id == scryfall_id).where(Card.foil == foil)).scalar()

    if existing_card:
        existing_card.quantity += 1
        message = f"{existing_card.name}'s quantity has been increased"
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

            if 'name' in data:
                name = data['name']
            if 'set' in data:
                set_id = data['set'].upper()
            if 'collector_number' in data:
                collector_number = data['collector_number']
            if 'color_identity' in data:
                if data['color_identity'] != []:
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

            new_card = Card(
                name=name,
                set_id=set_id,
                quantity=1,
                foil=foil,
                collector_number=collector_number,
                scryfall_id=scryfall_id,
                color_identity=color_identity,
                type_line=type_line,
                cmc=cmc,
                power=power,
                toughness=toughness,
                rarity=rarity,
                text=text
            )
            db.session.add(new_card)
            message = f"{name} has been added to your collection"
        else:
            error = "An error has occured when trying to add the card"

    db.session.commit()
    return redirect(url_for('add_card', message=message, error=error))

@app.route("/card/import", methods=['GET', 'POST'])
def import_cards():
    if request.method == 'GET':
        return render_template("import.html")
    else:
        message = None
        error = None
        errors = []

        if request.form.get('cardList'):
            cardList = request.form.get('cardList')
            cardList = cardList.strip()
            for line in cardList.split('\n'):
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

                                new_card = Card(
                                    name=name,
                                    set_id=set_id,
                                    quantity=quantity,
                                    foil=foil,
                                    collector_number=collector_number,
                                    scryfall_id=scryfall_id,
                                    color_identity=color_identity,
                                    type_line=type_line,
                                    cmc=cmc,
                                    power=power,
                                    toughness=toughness,
                                    rarity=rarity,
                                    text=text
                                )
                                db.session.add(new_card)
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
            error = "A card list is required to import"

        if not error:
            db.session.commit()
            message = "Successfully imported all cards to collection"
        elif error == True:
            error = "Unable to retrive the following cards from Scryfall. No cards have been imported."
        
        if len(errors) == 0:
            errors = None
        else:
            errors = "|".join(errors)
            
        return redirect(url_for("import_cards", message=message, error=error, errors=errors))

@app.route('/card/<card_id>/delete')
def delete_card(card_id):
    # Delete card associations
    db.session.execute(db.delete(DeckCard).where(DeckCard.card_id == card_id))

    # Delete card
    card = db.get_or_404(Card, card_id)
    db.session.delete(card)

    db.session.commit()
    return render_template("delete-card.html", message=f"{card.name} has been deleted")

@app.route('/card/<card_id>/quantity', methods=['POST'])
def edit_card_quantity(card_id):
    if request.form.get('quantity'):
        card = db.get_or_404(Card, card_id)
        card.quantity = request.form.get('quantity')
        db.session.commit()
        return redirect(url_for('card', id=card_id, message=f"The quantity has been increased to {request.form.get('quantity')}"))
    else:
        return redirect(url_for('card', id=card_id, error=f"A quantity is required to update"))
    
@app.route('/card/<card_id>/decks')
def card_decks(card_id):
    card = db.get_or_404(Card, card_id)
    return render_template('card-decks.html', card=card)

@app.route("/decks")
def decks():
    decks = db.session.execute(db.select(Deck).order_by(Deck.id.desc())).scalars().all()
    return render_template("decks.html", decks=decks)

@app.route("/decks/add", methods=['GET', 'POST'])
def add_deck():
    if request.method == 'GET':
        return render_template("add-deck.html")
    else:
        if request.form.get('name'):
            deck = Deck(name=request.form.get('name'))
            db.session.add(deck)
            db.session.commit()
            return redirect(url_for('deck', id=deck.id))
        else:
            return render_template("add-deck.html", error='A deck name is required!')
        
@app.route('/deck/<id>', methods=['GET', 'POST'])
def deck(id):
    deck = db.get_or_404(Deck, id)
    if request.method == 'GET':
        return render_template("deck.html", deck=deck)
    else:
        deck.plains = request.form.get('plains')
        deck.island = request.form.get('island')
        deck.swamp = request.form.get('swamp')
        deck.mountain = request.form.get('mountain')
        deck.forest = request.form.get('forest')
        db.session.commit()
        return render_template("deck.html", deck=deck)

@app.route('/deck/<deck_id>/card/<card_id>/add')
def add_card_to_deck(deck_id, card_id):
    deck = db.get_or_404(Deck, deck_id)
    card = db.get_or_404(Card, card_id)
    deck_card = DeckCard()
    deck_card.card = card
    deck.cards.append(deck_card)
    db.session.commit()
    return redirect(url_for('card', id=card_id, message=f'{card.name} has been added to deck {deck.name}'))

@app.route('/deck/<deck_id>/card/<card_id>/assoc/<assoc_id>/remove')
def remove_card_from_deck(deck_id, card_id, assoc_id):
    card = db.get_or_404(Card, card_id)
    db.session.execute(db.delete(DeckCard).where(DeckCard.id == assoc_id))
    db.session.commit()
    return redirect(url_for('deck', id=deck_id, message=f'{card.name} has been removed from this deck'))

@app.route('/deck/<deck_id>/assoc/<assoc_id>/commander/set')
def set_commander_for_deck(deck_id, assoc_id):
    assoc = db.session.execute(db.select(DeckCard).where(DeckCard.id == assoc_id)).scalar()
    assoc.is_commander = True
    db.session.commit()
    return redirect(url_for('deck', id=deck_id))

@app.route('/deck/<deck_id>/assoc/<assoc_id>/commander/unset')
def unset_commander_for_deck(deck_id, assoc_id):
    assoc = db.session.execute(db.select(DeckCard).where(DeckCard.id == assoc_id)).scalar()
    assoc.is_commander = False
    db.session.commit()
    return redirect(url_for('deck', id=deck_id))

@app.route('/deck/<deck_id>/delete')
def delete_deck(deck_id):
    # Delete card associations
    db.session.execute(db.delete(DeckCard).where(DeckCard.deck_id == deck_id))

    # Delete deck
    deck = db.get_or_404(Deck, deck_id)
    db.session.delete(deck)

    db.session.commit()
    return redirect(url_for('decks', message=f"{deck.name} has been deleted"))

@app.route('/search/autocomplete', methods=['POST'])
def autocomplete():
    if request.form.get("query"):
        cards = db.session.execute(db.select(Card.name).where(Card.name.like(f'%{request.form.get("query")}%'))).scalars().all()
        return cards

@app.errorhandler(404) 
def not_found(error):
    return render_template("404.html")
