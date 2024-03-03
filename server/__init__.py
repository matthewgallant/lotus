from flask import Flask, render_template

from config import Config
from server.extensions import db

from server.main import bp as main_bp
from server.search import bp as search_bp
from server.decks import bp as decks_bp
from server.cards import bp as cards_bp

def create_app(config_class=Config):
    server = Flask(__name__)
    server.config.from_object(config_class)

    # Initialize database
    db.init_app(server)

    # Register blueprints
    server.register_blueprint(main_bp, url_prefix='/api')
    server.register_blueprint(search_bp, url_prefix='/search')
    server.register_blueprint(decks_bp, url_prefix='/decks')
    server.register_blueprint(cards_bp, url_prefix='/cards')

    @server.errorhandler(404) 
    def not_found(error):
        return render_template("404.html")

    return server
