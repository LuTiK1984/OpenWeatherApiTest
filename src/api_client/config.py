import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OWM_API_KEY")
BASE_URL = os.getenv("OWM_BASE_URL", "https://api.openweathermap.org")