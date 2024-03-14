from datetime import datetime
from app.extensions import db

class Card(db.Model):
    __tablename__ = "cards"

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(250), nullable=False)
    set_id = db.Column(db.String(10))
    quantity = db.Column(db.Integer)
    foil = db.Column(db.String(20))
    collector_number = db.Column(db.String(10))
    scryfall_id = db.Column(db.String(50), nullable=False)
    color_identity = db.Column(db.String(20))
    type_line = db.Column(db.String(250))
    cmc = db.Column(db.Integer)
    power = db.Column(db.String(10))
    toughness = db.Column(db.String(10))
    rarity = db.Column(db.String(10))
    text = db.Column(db.String(500))
    created_on = db.Column(db.DateTime, nullable=False)

    decks = db.relationship('DeckCard', back_populates='card')

    def __init__(self, user_id, name, set_id, quantity, foil, collector_number, scryfall_id, color_identity, type_line, cmc, power, toughness, rarity, text):
        self.user_id = user_id
        self.name = name
        self.set_id = set_id
        self.quantity = quantity
        self.foil = foil
        self.collector_number = collector_number
        self.color_identity = color_identity
        self.scryfall_id = scryfall_id
        self.type_line = type_line
        self.cmc = cmc
        self.power = power
        self.toughness = toughness
        self.rarity = rarity
        self.text = text
        self.created_on = datetime.now()

    def __repr__(self):
        return self.name
