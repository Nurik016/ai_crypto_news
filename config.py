#config.py
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")
COINMARKETCAP_API_KEY = os.getenv("COINMARKETCAP_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not NEWSDATA_API_KEY:
    print("Warning: NEWSDATA_API_KEY not found in .env file.")
if not COINMARKETCAP_API_KEY:
    print("Warning: COINMARKETCAP_API_KEY not found in .env file.")
if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY not found in .env file.")


COINMARKETCAP_API_URL = "https://pro-api.coinmarketcap.com"
NEWSDATA_API_URL = "https://newsdata.io/api/1/news"

DEFAULT_NEWS_LANGUAGE = "en"
