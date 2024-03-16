from datetime import datetime
from app.extensions import db

class Card(db.Model):
    __tablename__ = "cards"

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    card_details_id = db.Column(db.Integer, db.ForeignKey('cards_details.id'), nullable=False)
    quantity = db.Column(db.Integer)
    foil = db.Column(db.String(20))
    created_on = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User')
    details = db.relationship('CardDetails')
    
    # Only get active (not archived) decks
    decks = db.relationship(
        'DeckCard',
        back_populates='card',
        primaryjoin="and_(Card.id == DeckCard.card_id, DeckCard.board.in_(('m', 's')))"
    )

    def __init__(self, user_id, card_details_id, quantity, foil):
        self.user_id = user_id
        self.card_details_id = card_details_id
        self.quantity = quantity
        self.foil = foil
        self.created_on = datetime.now()

    def __repr__(self):
        return f"{self.user} -> {self.details}"
