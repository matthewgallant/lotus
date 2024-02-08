import os
import urllib.parse

from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class Cards(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    set_id: Mapped[str] = mapped_column()
    quantity: Mapped[int] = mapped_column()
    foil: Mapped[str] = mapped_column()
    variation: Mapped[str] = mapped_column()
    collector_number: Mapped[int] = mapped_column()
    scryfall_id: Mapped[str] = mapped_column()
    color_identity: Mapped[str] = mapped_column()
    type_line: Mapped[str] = mapped_column()
    cmc: Mapped[int] = mapped_column()
    power: Mapped[int] = mapped_column()
    toughness: Mapped[int] = mapped_column()
    rarity: Mapped[str] = mapped_column()

# Create the app
app = Flask(__name__)

# Load databae path from .env
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']

# Initialize the app with the database
db.init_app(app)

def handle_search():
    query = db.select(Cards).group_by(Cards.name)

    # Handle color searches
    if request.args.get('name'):
        query = query.where(Cards.name.like(f'%{request.args.get("name")}%'))
    if request.args.get('color'):
        colors = request.args.get('color').split(',')
        core_colors = ['w', 'u', 'b', 'r', 'g']
        if 'un' in colors:
            query = query.where(Cards.color_identity == None, Cards.type_line.notlike('land'))
        else:
            for color in core_colors:
                if color in colors:
                    query = query.where(Cards.color_identity.contains(color))
                else:
                    query = query.where(Cards.color_identity.notlike(f'%{color}%'))
    if request.args.get('type'):
        query = query.where(Cards.type_line.like(f'%{request.args.get("type")}%'))
    
    print(query)
    
    return db.paginate(query, per_page=12)

@app.route("/")
def home():
    collection_total = db.session.query(Cards).count()
    return render_template("home.html", collection_total=collection_total)

@app.route("/search")
def search():
    return render_template("search.html")

@app.route("/results", methods=['GET', 'POST'])
def results():
    if request.method == 'POST':
        # Process POST data
        params = {}
        if request.form.get('name'):
            params['name'] = request.form.get('name')
        if len(request.form.getlist('color')) > 0:
            params['color'] = ",".join(request.form.getlist("color"))
        if request.form.get('type'):
            params['type'] = request.form.get('type')
        
        # Redirect to GET url
        return redirect(f'/results?{urllib.parse.urlencode(params)}')
    else:
        cards = handle_search()

        # Redirect to card page if only 1 card is found
        if cards.total == 1:
            return redirect(f'/card/{cards.items[0].id}')
        else:
            return render_template("results.html", cards=cards)

@app.route("/api/cards")
def api_cards():
    cards = handle_search()
    return render_template("api/cards.html", cards=cards)

@app.route("/card/<id>")
def card(id):
    card = db.get_or_404(Cards, id)
    cards = db.session.execute(db.select(Cards).where(Cards.name == card.name)).scalars().all()
    return render_template("card.html", card=card, cards=cards)

@app.errorhandler(404) 
def not_found(error):
    return render_template("404.html")
