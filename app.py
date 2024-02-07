import os
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

# Create the app
app = Flask(__name__)

# Load databae path from .env
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']

# Initialize the app with the database
db.init_app(app)

def handle_search():
    query = db.select(Cards).group_by(Cards.name)

    # Handle color searches
    if request.args.get('color'):
        colors = request.args.get('color').split(',')
        for color in colors:
            if color != 'un':
                query = query.where(Cards.color_identity.contains(color))
            else:
                query = query.where(Cards.color_identity == None)
    
    return db.paginate(query, per_page=12)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/search")
def search():
    return render_template("search.html")

@app.route("/results", methods=['GET', 'POST'])
def results():
    if request.method == 'POST':
        # Build GET url and then redirect
        url = '/results?'
        if len(request.form.getlist('color')) > 0:
            url += f'color={",".join(request.form.getlist("color"))}'
        return redirect(url)
    else:
        cards = handle_search()
        return render_template("results.html", cards=cards)

@app.route("/api/cards")
def api_cards():
    cards = handle_search()
    return render_template("api/cards.html", cards=cards)
