from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_class=Config):

    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Redirect here if not logged in
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Import models here (after db is created)
    with app.app_context():
        from app import models
    
    from app.routes import main, auth, bugs, battles
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(bugs.bp)
    app.register_blueprint(battles.bp)
    
    return app
