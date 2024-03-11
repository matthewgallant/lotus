from flask import render_template, redirect, request, url_for
from flask_login import login_required
from sqlalchemy import func

from app.search import bp
from app.extensions import db

from app.models.card import Card

def handle_search():
    unique_named_cards = db.select(func.min(Card.id)).group_by(Card.name)
    query = db.select(Card).where(Card.id.in_(unique_named_cards))

    if request.args.get('name'):
        query = query.where(Card.name.like(f'%{request.args.get("name")}%'))
    if request.args.get('text'):
        query = query.where(Card.text.like(f'%{request.args.get("text")}%'))
    if request.args.get('type'):
        query = query.where(Card.type_line.like(f'%{request.args.get("type")}%'))
    if request.args.get('set'):
        query = query.where(Card.set_id == request.args.get('set'))
    if request.args.get('rarity'):
        query = query.where(Card.rarity == request.args.get('rarity'))
    if request.args.get('color'):
        colors = request.args.get('color').split(',')
        core_colors = ['w', 'u', 'b', 'r', 'g']
        if 'un' in colors:
            query = query.where(Card.color_identity == None, Card.type_line.notlike('land'))
        else:
            for color in core_colors:
                if color in colors:
                    query = query.where(Card.color_identity.contains(color))
                else:
                    query = query.where(Card.color_identity.notlike(f'%{color}%'))
    if request.args.get('cmc') and request.args.get('cmcType'):
        cmc = request.args.get('cmc')
        cmcType = request.args.get('cmcType')

        if cmcType == 'lessThan':
            query = query.where(Card.cmc < cmc)
        elif cmcType == 'lessThanEqualTo':
            query = query.where(Card.cmc <= cmc)
        elif cmcType == 'equalTo':
            query = query.where(Card.cmc == cmc)
        elif cmcType == 'greaterThanEqualTo':
            query = query.where(Card.cmc >= cmc)
        elif cmcType == 'greaterThan':
            query = query.where(Card.cmc > cmc)
    
    return db.paginate(query, per_page=12)

@bp.route("/")
@login_required
def search():
    sets = db.session.execute(db.select(Card.set_id).group_by(Card.set_id))
    return render_template("search/search.html", sets=sets)

@bp.route("/results", methods=['GET', 'POST'])
@login_required
def results():
    if request.method == 'POST':
        params = {}

        # Process POST data
        if request.form.get('name'):
            params['name'] = request.form.get('name').strip().lower()
        if request.form.get('text'):
            params['text'] = request.form.get('text').strip().lower()
        if request.form.get('type'):
            params['type'] = request.form.get('type').strip().lower()
        if request.form.get('set'):
            params['set'] = request.form.get('set').strip().upper()
        if request.form.get('rarity'):
            params['rarity'] = request.form.get('rarity')
        if len(request.form.getlist('color')) > 0:
            params['color'] = ",".join(request.form.getlist("color"))
        if request.form.get('cmc') and request.form.get('cmcType'):
            params['cmc'] = int(request.form.get('cmc'))
            params['cmcType'] = request.form.get('cmcType')
        
        # Redirect to GET url
        return redirect(url_for('search.results', **params))
    else:
        cards = handle_search()

        # Redirect to card page if only 1 card is found
        if cards.total == 1:
            return redirect(url_for('cards.card', id=cards.items[0].id))
        else:
            return render_template("search/results.html", cards=cards)
        
@bp.route("/api/cards")
@login_required
def api_cards():
    cards = handle_search()
    return render_template("search/api/cards.html", cards=cards)
