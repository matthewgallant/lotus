from flask import Flask, render_template

from config import Config
from app.extensions import db

from app.main import bp as main_bp
from app.decks import bp as decks_bp
from app.cards import bp as cards_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize database
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(decks_bp, url_prefix='/decks')
    app.register_blueprint(cards_bp, url_prefix='/cards')

    @app.errorhandler(404) 
    def not_found(error):
        return render_template("404.html")

    return app
