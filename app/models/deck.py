from app.extensions import db
from app.models.deck_card import DeckCard
from sqlalchemy import and_

class Deck(db.Model):
    __tablename__ = "decks"

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    plains = db.Column(db.Integer)
    island = db.Column(db.Integer)
    swamp = db.Column(db.Integer)
    mountain = db.Column(db.Integer)
    forest = db.Column(db.Integer)

    mainboard = db.relationship(
        'DeckCard',
        back_populates='deck',
        order_by='DeckCard.is_commander.desc()',
        primaryjoin=and_(DeckCard.deck_id == id, DeckCard.board == 'm')
    )
    sideboard = db.relationship(
        'DeckCard',
        back_populates='deck',
        order_by='DeckCard.is_commander.desc()',
        primaryjoin=and_(DeckCard.deck_id == id, DeckCard.board == 's')
    )
