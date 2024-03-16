from datetime import datetime
from app.extensions import db

class DeckCard(db.Model):
    __tablename__ = "decks_cards"

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    deck_id = db.Column(db.Integer, db.ForeignKey('decks.id'), nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey('cards.id'), nullable=False)
    is_commander = db.Column(db.Boolean)
    board = db.Column(db.String(2))
    created_on = db.Column(db.DateTime, nullable=False)

    deck = db.relationship('Deck')
    card = db.relationship('Card', back_populates='decks')

    def __init__(self, deck_id, card_id, board):
        self.deck_id = deck_id
        self.card_id = card_id
        self.board = board
        self.created_on = datetime.now()

    def __repr__(self):
        return f"{self.deck} -> {self.card}"
