from app.extensions import db

class Card(db.Model):
    __tablename__ = "cards"

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
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
    text = db.Column(db.String)

    decks = db.relationship('DeckCard', back_populates='card')

    def __str__(self):
        return self.name
