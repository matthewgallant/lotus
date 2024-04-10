from flask import Flask, render_template

from config import Config
from app.extensions import db, bcrypt, login_manager

from app.main import bp as main_bp
from app.accounts import bp as account_bp
from app.search import bp as search_bp
from app.decks import bp as decks_bp
from app.cards import bp as cards_bp
from app.api.cards import bp as api_cards_bp
from app.api.decks import bp as api_decks_bp

from app.models.user import User

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Config extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "account.login"

    # Create tables if needed
    with app.app_context():
        db.create_all()
    
    # Create login user loader
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.execute(db.select(User).where(User.id == int(user_id))).scalar_one_or_none()

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(account_bp, url_prefix='/account')
    app.register_blueprint(search_bp, url_prefix='/search')
    app.register_blueprint(decks_bp, url_prefix='/decks')
    app.register_blueprint(cards_bp, url_prefix='/cards')
    app.register_blueprint(api_cards_bp, url_prefix='/api/cards')
    app.register_blueprint(api_decks_bp, url_prefix='/api/decks')

    # Handle 404s
    @app.errorhandler(404) 
    def not_found(error):
        return render_template("404.html"), 404
    
    @app.after_request
    def add_security_headers(resp):
        resp.headers['Content-Security-Policy'] = "default-src 'self' https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://fonts.googleapis.com https://fonts.gstatic.com https://api.scryfall.com; img-src 'self' https://api.scryfall.com https://cards.scryfall.io data:;"
        return resp

    return app
