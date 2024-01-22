"""Flask & Spotify API configuration variables."""
from os import environ, path
from dotenv import load_dotenv

BASE_DIR = path.abspath(path.dirname(__file__))
load_dotenv(path.join(BASE_DIR, ".env"))

class Config: 
    """Set configuration from .env file."""
    
    # General Config
    ENVIRONMENT = environ.get("ENVIRONMENT")

    # Flask Config
    FLASK_APP = "timetable_input_service.py"
    FLASK_DEBUG = environ.get("FLASK_DEBUG")
    SECRET_KEY = environ.get("SECRET_KEY")
    
    FLASK_ADDRESS = environ.get("FLASK_ADDRESS")
    PORT = environ.get("PORT")