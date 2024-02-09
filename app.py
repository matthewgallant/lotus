import os
import urllib.parse

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class DeckCard(db.Model):
    __tablename__ = "decks_cards"

    id = db.Column(db.Integer, primary_key=True)
    deck_id = db.Column(db.Integer, db.ForeignKey('decks.id'))
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'))
    is_commander = db.Column(db.Boolean)

    deck = db.relationship('Deck', back_populates='cards')
    card = db.relationship('Card', back_populates='decks')

class Deck(db.Model):
    __tablename__ = "decks"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    plains = db.Column(db.Integer)
    island = db.Column(db.Integer)
    swamp = db.Column(db.Integer)
    mountain = db.Column(db.Integer)
    forest = db.Column(db.Integer)

    cards = db.relationship('DeckCard', back_populates='deck', order_by='DeckCard.is_commander.desc()')

class Card(db.Model):
    __tablename__ = "cards"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    set_id = db.Column(db.String)
    quantity = db.Column(db.Integer)
    foil = db.Column(db.String)
    variation = db.Column(db.String)
    collector_number = db.Column(db.Integer)
    scryfall_id = db.Column(db.String)
    color_identity = db.Column(db.String)
    type_line = db.Column(db.String)
    cmc = db.Column(db.Integer)
    power = db.Column(db.Integer)
    toughness = db.Column(db.Integer)
    rarity = db.Column(db.String)

    decks = db.relationship('DeckCard', back_populates='card')

# Create the app
app = Flask(__name__)

# Load databae path from .env
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']

# Initialize the app with the database
db.init_app(app)

def handle_search():
    query = db.select(Card).group_by(Card.name)

    # Handle color searches
    if request.args.get('name'):
        query = query.where(Card.name.like(f'%{request.args.get("name")}%'))
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
    if request.args.get('type'):
        query = query.where(Card.type_line.like(f'%{request.args.get("type")}%'))
    
    return db.paginate(query, per_page=12)

@app.route("/")
def home():
    collection_total = db.session.query(Card).count()
    return render_template("home.html", collection_total=collection_total)

@app.route("/search")
def search():
    return render_template("search.html")

@app.route("/results", methods=['GET', 'POST'])
def results():
    if request.method == 'POST':
        # Process POST data
        params = {}
        if request.form.get('name'):
            params['name'] = request.form.get('name')
        if len(request.form.getlist('color')) > 0:
            params['color'] = ",".join(request.form.getlist("color"))
        if request.form.get('type'):
            params['type'] = request.form.get('type')
        
        # Redirect to GET url
        return redirect(f'/results?{urllib.parse.urlencode(params)}')
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
    decks = db.session.execute(db.select(Deck)).scalars().all()
    return render_template("card.html", card=card, cards=cards, decks=decks)

@app.route("/decks")
def decks():
    decks = db.session.execute(db.select(Deck)).scalars().all()
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

@app.errorhandler(404) 
def not_found(error):
    return render_template("404.html")
