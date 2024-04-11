import requests
import json
import time

from app.extensions import db, scheduler
from app.models.card_details import CardDetails

@scheduler.task('cron', id='update_prices', minute=0, hour=0)
def update_prices():
    # Get app context to access the db
    with scheduler.app.app_context():
        # Get all card details
        cards = db.session.execute(db.select(CardDetails)).scalars().all()

        # Chunk cards for Scryfall
        chunked_cards = [cards[i:i + 75] for i in range(0, len(cards), 75)]

        # Process chunks
        for chunk in chunked_cards:
            # Create JSON formatted for Scryfall
            payload = { "identifiers": list(map(lambda s: { "id": s.scryfall_id }, chunk)) }

            # Post to Scryfall
            res = requests.post("https://api.scryfall.com/cards/collection", json=payload)
            if res.status_code == 200:
                data = json.loads(res.text)
                for card in data['data']:
                    # Get db card object matching this Scryfall data
                    db_card = list(filter(lambda c: c.scryfall_id == card['id'], cards))[0]
                    if db_card:
                        # Store price data
                        db_card.price_regular = card['prices']['usd']
                        db_card.price_foil = card['prices']['usd_foil']
                        db_card.price_etched = card['prices']['usd_etched']
            
            # Sleep before continuing to be polite
            time.sleep(1)
        
        # Save
        db.session.commit()
