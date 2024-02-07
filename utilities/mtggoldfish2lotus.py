import argparse
import csv
import sqlite3
import requests
import json
import urllib.parse

# Collect arguments
parser = argparse.ArgumentParser(prog='mtggoldfish2lotus.py', description='MTG Goldfish CSV to Lotus SQLite Database Importer')
parser.add_argument('-csv', help='CSV file from MTG Goldfish', type=argparse.FileType('r'), required=True)
parser.add_argument('-db', help='SQLite database file with a configured cards table', required=True)
args = parser.parse_args()

# Open DB connection
con = sqlite3.connect(args.sqlite)
cur = con.cursor()

# Open CSV reader
reader = csv.reader(args.csv, delimiter=',')

# Skip header row
next(reader, None)

for row in reader:
    # Parse each column
    name = row[0]
    set_id = row[1]
    set_name = row[2]
    quantity = int(row[3])
    foil = row[4]
    variation = row[5]
    collector_number = row[6]
    scryfall_id = row[7]

    print(f'Importing {name}')

    # Gather additional details from Scryfall
    color_identity = None

    if scryfall_id:
        res = requests.get(f'https://api.scryfall.com/cards/{scryfall_id}')
    elif set_id and collector_number:
        res = requests.get(f'https://api.scryfall.com/cards/{set_id}/{collector_number}')
    else:
        res = requests.get(f'https://api.scryfall.com/cards/named?fuzzy={urllib.parse.quote_plus(name)}')
    
    data = json.loads(res.text)
    
    if 'id' in data:
        scryfall_id = data['id']
    if 'color_identity' in data:
        if data['color_identity'] != '':
            color_identity = ",".join(data['color_identity'])

    # Insert new row
    if scryfall_id:
        cur.execute(
            "INSERT INTO cards (name, set_id, quantity, foil, variation, collector_number, scryfall_id, color_identity) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (name, set_id, quantity, foil, variation, collector_number, scryfall_id, color_identity)
        )

# Commit and clean up
con.commit()
cur.close()
con.close()
