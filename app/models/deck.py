from datetime import datetime
from sqlalchemy import and_
from app.extensions import db
from app.models.deck_card import DeckCard

class Deck(db.Model):
    __tablename__ = "decks"

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(250), nullable=False)
    archived = db.Column(db.Boolean)
    plains = db.Column(db.Integer)
    island = db.Column(db.Integer)
    swamp = db.Column(db.Integer)
    mountain = db.Column(db.Integer)
    forest = db.Column(db.Integer)
    notes = db.Column(db.String(5000))
    created_on = db.Column(db.DateTime, nullable=False)

    mainboard = db.relationship(
        'DeckCard',
        back_populates='deck',
        order_by='DeckCard.is_commander.desc()',
        primaryjoin=and_(DeckCard.deck_id == id, DeckCard.board.in_(('m', 'am')))
    )
    sideboard = db.relationship(
        'DeckCard',
        back_populates='deck',
        overlaps='mainboard',
        order_by='DeckCard.is_commander.desc()',
        primaryjoin=and_(DeckCard.deck_id == id, DeckCard.board.in_(('s', 'as')))
    )

    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name
        self.created_on = datetime.now()

    def __repr__(self):
        return f"{self.name} ({self.id})"
