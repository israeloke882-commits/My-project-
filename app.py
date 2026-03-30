from flask import Flask
import os
import sys
import logging
from flask_login import LoginManager
from database import db
import models
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.DEBUG)

# Compatibility Check
if sys.version_info >= (3, 14):
    logging.error("Incompatible Python version detected (3.14+). "
                  "Please use Python 3.11 or 3.12 for TensorFlow compatibility.")
elif sys.version_info.major == 3 and sys.version_info.minor == 11:
    logging.info(f"Verified Python {sys.version} - Compatibility confirmed.")


os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)

app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-for-local-development")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["GOOGLE_CLIENT_ID"] = os.environ.get("GOOGLE_CLIENT_ID")
app.config["GOOGLE_CLIENT_SECRET"] = os.environ.get("GOOGLE_CLIENT_SECRET")

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main.login'

from routes import main
from gmail_routes import gmail_blueprint
from news_routes import news_blueprint

app.register_blueprint(main)
app.register_blueprint(gmail_blueprint, url_prefix="/google")
app.register_blueprint(news_blueprint)

@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(int(user_id))

with app.app_context():
    try:
        db.create_all()
        from models import User # Ensure models are registered
        logging.info("Database initialized and tables verified.")
    except Exception as e:
        logging.error(f"Database initialization failed: {e}")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
