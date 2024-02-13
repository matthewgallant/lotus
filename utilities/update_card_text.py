import argparse
import sqlite3
import requests
import time

# Collect arguments
parser = argparse.ArgumentParser(prog='update_card_text.py', description='Updates the local database with card text from Scryfall')
parser.add_argument('-db', help='SQLite database file with a configured cards table', required=True)
args = parser.parse_args()

# Open DB connection
con = sqlite3.connect(args.db)
cur = con.cursor()

cards = cur.execute("SELECT id, name, scryfall_id FROM cards").fetchall()
for card in cards:
    id = card[0]
    name = card[1]
    scryfall_id = card[2]

    print(f"Updating {name}")

    # Update card using oracle text from Scryfall
    res = requests.get(f'https://api.scryfall.com/cards/{scryfall_id}')
    if res.status_code == 200:
        data = res.json()
        if 'oracle_text' in data:
            cur.execute("UPDATE cards SET text = ? WHERE id = ?", (data['oracle_text'], id))
    
    # Delay requests per Scryfall's rules
    time.sleep(0.1)

# Commit and clean up
con.commit()
cur.close()
con.close()
