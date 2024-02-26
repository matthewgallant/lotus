from app.extensions import db

class DeckCard(db.Model):
    __tablename__ = "decks_cards"

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    deck_id = db.Column(db.Integer, db.ForeignKey('decks.id'), nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), nullable=False)
    is_commander = db.Column(db.Boolean)
    board = db.Column(db.String)

    deck = db.relationship('Deck')
    card = db.relationship('Card', back_populates='decks')
