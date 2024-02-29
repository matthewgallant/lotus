BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "cards" (
	"id"	INTEGER NOT NULL,
	"name"	TEXT NOT NULL,
	"set_id"	TEXT,
	"quantity"	INTEGER,
	"foil"	TEXT,
	"collector_number"	INTEGER,
	"scryfall_id"	TEXT NOT NULL,
	"color_identity"	TEXT,
	"type_line"	TEXT,
	"cmc"	INTEGER,
	"power"	INTEGER,
	"toughness"	INTEGER,
	"rarity"	TEXT,
	"text"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "decks" (
	"id"	INTEGER NOT NULL,
	"name"	TEXT NOT NULL,
	"plains"	INTEGER,
	"island"	INTEGER,
	"swamp"	INTEGER,
	"mountain"	INTEGER,
	"forest"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "decks_cards" (
	"id"	INTEGER NOT NULL,
	"deck_id"	INTEGER NOT NULL,
	"card_id"	INTEGER NOT NULL,
	"is_commander"	INTEGER,
	"board"	TEXT,
	PRIMARY KEY("id" AUTOINCREMENT)
);
COMMIT;
