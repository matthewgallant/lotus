from flask import Blueprint, render_template, redirect, request, url_for
from flask_login import login_required, current_user
from sqlalchemy import func

from app.extensions import db
from app.models.card import Card
from app.models.card_details import CardDetails

search_bp = Blueprint('search', __name__, template_folder="templates")

@search_bp.route("/", methods=['GET', 'POST'])
@login_required
def search():
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
        # Get sets owned by user
        query = db.select(CardDetails.set_id).join(Card.details).where(Card.user_id == current_user.id).group_by(CardDetails.set_id)
        sets = db.session.execute(query)

        return render_template("search.html", sets=sets)

@search_bp.route("/results")
@login_required
def results():
    subquery = db.select(func.min(Card.id)).join(Card.details).where(Card.user_id == current_user.id).group_by(CardDetails.name)
    query = db.select(Card).where(Card.id.in_(subquery)).join(Card.details)

    # Process URL args
    if request.args.get('name'):
        query = query.where(CardDetails.name.like(f'%{request.args.get("name")}%'))
    if request.args.get('text'):
        query = query.where(CardDetails.text.like(f'%{request.args.get("text")}%'))
    if request.args.get('type'):
        query = query.where(CardDetails.type_line.like(f'%{request.args.get("type")}%'))
    if request.args.get('set'):
        query = query.where(CardDetails.set_id == request.args.get('set'))
    if request.args.get('rarity'):
        query = query.where(CardDetails.rarity == request.args.get('rarity'))
    if request.args.get('color'):
        colors = request.args.get('color').split(',')
        core_colors = ['w', 'u', 'b', 'r', 'g']
        if 'un' in colors:
            query = query.where(CardDetails.color_identity == None, CardDetails.type_line.notlike('land'))
        else:
            for color in core_colors:
                if color in colors:
                    query = query.where(CardDetails.color_identity.contains(color))
                else:
                    query = query.where(CardDetails.color_identity.notlike(f'%{color}%'))
    if request.args.get('cmc') and request.args.get('cmcType'):
        cmc = request.args.get('cmc')
        cmcType = request.args.get('cmcType')

        if cmcType == 'lessThan':
            query = query.where(CardDetails.cmc < cmc)
        elif cmcType == 'lessThanEqualTo':
            query = query.where(CardDetails.cmc <= cmc)
        elif cmcType == 'equalTo':
            query = query.where(CardDetails.cmc == cmc)
        elif cmcType == 'greaterThanEqualTo':
            query = query.where(CardDetails.cmc >= cmc)
        elif cmcType == 'greaterThan':
            query = query.where(CardDetails.cmc > cmc)
    
    # Get paginated card results
    cards = db.paginate(query, per_page=12)

    # Redirect to card page if only 1 card is found
    if cards.total == 1:
        return redirect(url_for('cards.card', id=cards.items[0].id))
    else:
        if request.args.get("page"):
            # Page is only used in API calls
            return render_template("api/cards.html", cards=cards)
        else:
            return render_template("results.html", cards=cards)
        