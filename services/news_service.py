# news_service.py
import requests
import json

from config import DEFAULT_NEWS_LANGUAGE, NEWSDATA_API_KEY, NEWSDATA_API_URL

# --- Newsdata.io API Functions ---

def get_newsdata_io_news(coin_name, language=DEFAULT_NEWS_LANGUAGE, size=5):
    """
    Fetches news for a specific coin name from Newsdata.io.
    :param coin_name: The name of the cryptocurrency (e.g., "Bitcoin", "Ethereum").
    :param language: Language code (e.g., 'en', 'es').
    :param size: Number of articles to fetch.
    :return: List of news articles or None if an error occurs.
    """
    if not NEWSDATA_API_KEY:
        print("Error: NEWSDATA_API_KEY not set in config.")
        return None

    query = f'"{coin_name}" AND (cryptocurrency OR crypto OR blockchain)'
    params = {
        'apikey': NEWSDATA_API_KEY,
        'q': query,
        'language': language,
        'size': size
    }

    try:
        response = requests.get(NEWSDATA_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "success":
            articles_raw = data.get("results", [])
            articles = []
            for article_data in articles_raw:
                articles.append({
                    'title': article_data.get('title'),
                    'link': article_data.get('link'),
                    'description': article_data.get('description'),
                    'source_id': article_data.get('source_id'),
                    'published_at': article_data.get('pubDate'),
                    'keywords': article_data.get('keywords', [])
                })
            return articles
        else:
            # Handle API-specific errors from Newsdata.io
            error_info = data.get('results', {})
            error_message = error_info.get('message', 'Unknown Newsdata.io API error')
            if isinstance(error_info, list) and error_info: # sometimes error is a list
                 error_message = error_info[0]

            print(f"Newsdata.io API Error: {error_message}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching news from Newsdata.io: {e}")
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON response from Newsdata.io.")
        return None
