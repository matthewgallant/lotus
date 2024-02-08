import argparse
import csv
import sqlite3
import requests
import json
import time
import urllib.parse

# Collect arguments
parser = argparse.ArgumentParser(prog='mtggoldfish2lotus.py', description='MTG Goldfish CSV to Lotus SQLite Database Importer')
parser.add_argument('-csv', help='CSV file from MTG Goldfish', type=argparse.FileType('r'), required=True)
parser.add_argument('-db', help='SQLite database file with a configured cards table', required=True)
args = parser.parse_args()

# Open DB connection
con = sqlite3.connect(args.db)
cur = con.cursor()

# Open CSV reader
reader = csv.reader(args.csv, delimiter=',')

# Skip header row
next(reader, None)

# Collect errors
errors = []

for row in reader:
    # Parse each column that we care about
    name = row[0]
    set_id = row[1]
    quantity = int(row[3])
    foil = row[4]
    variation = row[5]
    collector_number = row[6]
    scryfall_id = row[7]

    # Set null defaults
    if name == '':
        name = None
    if set_id == '':
        set_id = None
    if quantity == '':
        quantity = None
    if foil == '':
        foil = None
    if variation == '':
        variation = None
    if collector_number == '':
        collector_number = None
    if scryfall_id == '':
        scryfall_id = None

    print(f'Importing: {name}')

    # Set null defaults for Scryfall data
    color_identity = None
    type_line = None
    cmc = None
    power = None
    toughness = None
    rarity = None

    # Attempt to locate card on Scryfall
    if scryfall_id:
        res = requests.get(f'https://api.scryfall.com/cards/{scryfall_id}')
    elif set_id and collector_number:
        res = requests.get(f'https://api.scryfall.com/cards/{set_id.lower()}/{collector_number}')
    elif set_id:
        res = requests.get(f'https://api.scryfall.com/cards/named?fuzzy={urllib.parse.quote_plus(name)}&set={set_id.lower()}')
    else:
        res = requests.get(f'https://api.scryfall.com/cards/named?fuzzy={urllib.parse.quote_plus(name)}')
    
    # Handle not finding the card
    if res.status_code != 200:
        print(f"There was an error finding '{name}' on Scryfall. Please enter that card's Scryfall ID to continue.")
        scryfall_id = input("Scryfall ID: ")
        res = requests.get(f'https://api.scryfall.com/cards/{scryfall_id}')
        if res.status_code != 200:
            errors.append(json.loads(res.text))
            print("Still can't find card data, skipping...")
            
            # Prevent inserting row if we can't find a card but still have a Scryfall id
            scryfall_id = None
    
    # Load data into dictionary
    data = json.loads(res.text)
    
    # Parse data from Scryfall
    if 'id' in data:
        scryfall_id = data['id']
    if 'color_identity' in data:
        if data['color_identity'] != []:
            color_identity = ",".join(data['color_identity'])
    if 'type_line' in data:
        type_line = data['type_line']
    if 'cmc' in data:
        cmc = data['cmc']
    if 'power' in data:
        power = data['power']
    if 'toughness' in data:
        toughness = data['toughness']
    if 'rarity' in data:
        rarity = data['rarity']
    if 'set' in data:
        set_id = data['set'].upper()
    if 'collector_number' in data:
        collector_number = data['collector_number']

    # Insert new row
    if scryfall_id:
        cur.execute(
            """
            INSERT INTO cards (
                name,
                set_id,
                quantity,
                foil,
                variation,
                collector_number,
                scryfall_id,
                color_identity,
                type_line,
                cmc,
                power,
                toughness,
                rarity
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (name, set_id, quantity, foil, variation, collector_number, scryfall_id, color_identity, type_line, cmc, power, toughness, rarity)
        )
    else:
        print(f"No Scryfall ID found for {name}")
        errors.append(data)
    
    # Delay requests per Scryfall's rules
    time.sleep(0.1)

# Commit and clean up
con.commit()
cur.close()
con.close()
