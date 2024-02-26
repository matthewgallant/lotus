from app.extensions import db

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
