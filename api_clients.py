# api_clients.py
import requests
import json
from config import (
    COINMARKETCAP_API_KEY, COINMARKETCAP_API_URL,
    NEWSDATA_API_KEY, NEWSDATA_API_URL,
    DEFAULT_NEWS_LANGUAGE, GEMINI_API_KEY # GEMINI_API_KEY not used here yet
)

# --- CoinMarketCap API Functions ---

def get_cmc_headers():
    """Returns the headers required for CoinMarketCap API calls."""
    if not COINMARKETCAP_API_KEY:
        print("Error: COINMARKETCAP_API_KEY not set.")
        return None
    return {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': COINMARKETCAP_API_KEY,
    }

def get_top_50_coins_cmc():
    """
    Fetches the top 50 cryptocurrencies by market cap from CoinMarketCap.
    Returns a list of dictionaries, each containing coin data, or None if an error occurs.
    """
    headers = get_cmc_headers()
    if not headers:
        return None

    url = f"{COINMARKETCAP_API_URL}/v1/cryptocurrency/listings/latest"
    parameters = {
        'start': '1',
        'limit': '50',
        'convert': 'USD'
    }

    try:
        response = requests.get(url, params=parameters, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
        data = response.json()

        if data.get('status', {}).get('error_code') == 0:
            coins = []
            for coin_data in data.get('data', []):
                coins.append({
                    'id': coin_data.get('id'),
                    'name': coin_data.get('name'),
                    'symbol': coin_data.get('symbol'),
                    'rank': coin_data.get('cmc_rank'),
                    'price_usd': coin_data.get('quote', {}).get('USD', {}).get('price'),
                    'market_cap_usd': coin_data.get('quote', {}).get('USD', {}).get('market_cap'),
                    'volume_24h_usd': coin_data.get('quote', {}).get('USD', {}).get('volume_24h')
                })
            return coins
        else:
            print(f"CoinMarketCap API Error: {data.get('status', {}).get('error_message')}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching top 50 coins from CoinMarketCap: {e}")
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON response from CoinMarketCap for top 50 coins.")
        return None

def get_coin_data_cmc(coin_symbol=None, coin_id=None):
    """
    Fetches market data for a specific cryptocurrency from CoinMarketCap
    using its symbol (e.g., "BTC") or CMC ID (e.g., 1).
    Returns a dictionary with coin data, or None if an error occurs or coin not found.
    """
    headers = get_cmc_headers()
    if not headers:
        return None
    if not coin_symbol and not coin_id:
        print("Error: You must provide either coin_symbol or coin_id for get_coin_data_cmc.")
        return None

    url = f"{COINMARKETCAP_API_URL}/v1/cryptocurrency/quotes/latest"
    parameters = {'convert': 'USD'}
    if coin_symbol:
        parameters['symbol'] = coin_symbol.upper()
    elif coin_id:
        parameters['id'] = str(coin_id)

    try:
        response = requests.get(url, params=parameters, headers=headers)
        response.raise_for_status()
        data = response.json()

        if data.get('status', {}).get('error_code') == 0:
            key_to_check = coin_symbol.upper() if coin_symbol else str(coin_id)
            
            if key_to_check in data.get('data', {}):
                coin_data_raw = data['data'][key_to_check]
                # If queried by symbol, CMC might return a list if multiple coins share the symbol
                # We'll take the first one, which is usually the most prominent.
                if isinstance(coin_data_raw, list):
                    if not coin_data_raw: return None # Empty list
                    coin_data_raw = coin_data_raw[0]
                
                return {
                    'id': coin_data_raw.get('id'),
                    'name': coin_data_raw.get('name'),
                    'symbol': coin_data_raw.get('symbol'),
                    'rank': coin_data_raw.get('cmc_rank'),
                    'price_usd': coin_data_raw.get('quote', {}).get('USD', {}).get('price'),
                    'market_cap_usd': coin_data_raw.get('quote', {}).get('USD', {}).get('market_cap'),
                    'volume_24h_usd': coin_data_raw.get('quote', {}).get('USD', {}).get('volume_24h'),
                    'percent_change_24h': coin_data_raw.get('quote', {}).get('USD', {}).get('percent_change_24h'),
                    'circulating_supply': coin_data_raw.get('circulating_supply'),
                    'total_supply': coin_data_raw.get('total_supply'),
                    'max_supply': coin_data_raw.get('max_supply'),
                    'last_updated': coin_data_raw.get('quote', {}).get('USD', {}).get('last_updated'),
                }
            else:
                print(f"Coin '{key_to_check}' not found in CoinMarketCap response.")
                return None
        else:
            print(f"CoinMarketCap API Error for '{coin_symbol or coin_id}': {data.get('status', {}).get('error_message')}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for '{coin_symbol or coin_id}' from CoinMarketCap: {e}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON response from CoinMarketCap for '{coin_symbol or coin_id}'.")
        return None

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

# --- Data Aggregation Function ---
def get_aggregated_coin_data(coin_identifier):
    """
    Aggregates market data and news for a given coin.
    :param coin_identifier: Can be a coin symbol (e.g., "BTC") or a coin name (e.g., "Bitcoin").
    :return: A dictionary containing aggregated data, or None if essential data can't be fetched.
    """
    print(f"\nAttempting to aggregate data for: {coin_identifier}")
    
    market_data = None
    news_articles = [] # Default to empty list
    
    # Try to get market data using the identifier as a symbol
    potential_symbol = coin_identifier.upper() # Assume it could be a symbol
    market_data = get_coin_data_cmc(coin_symbol=potential_symbol)
    
    coin_name_for_news = coin_identifier # Default to using the raw identifier for news
    
    if market_data:
        print(f"Successfully fetched market data for {market_data.get('name', potential_symbol)} from CMC.")
        coin_name_for_news = market_data.get('name', coin_identifier) # Use name from CMC for news query
    else:
        print(f"Could not fetch market data for '{potential_symbol}' using it as a symbol from CMC. Market data will be missing.")
        # If coin_identifier was "Bitcoin", coin_name_for_news remains "Bitcoin" for the news query

    # Get news from Newsdata.io using the determined/original coin name
    print(f"Fetching news for '{coin_name_for_news}' using Newsdata.io...")
    fetched_news = get_newsdata_io_news(coin_name=coin_name_for_news, size=3) # Fetch 3 news articles for brevity

    if fetched_news is not None: # Check if fetch was successful (returned a list)
        news_articles = fetched_news
        print(f"Fetched {len(news_articles)} news articles for {coin_name_for_news}.")
    else:
        # get_newsdata_io_news prints its own errors
        print(f"News fetching for '{coin_name_for_news}' resulted in no articles or an error. News data will be empty.")
        # news_articles remains an empty list

    # Only return something if we have at least some data
    if not market_data and not news_articles:
        print(f"Could not retrieve any meaningful data for {coin_identifier}.")
        return None

    aggregated_data = {
        "query_identifier": coin_identifier,
        "resolved_name_for_news": coin_name_for_news, # The name used for the news query
        "market_data": market_data, # This will be None if CMC fetch failed
        "news_articles": news_articles # This will be an empty list if news fetch failed or no news
    }
    
    return aggregated_data


# --- Main Test Block ---
if __name__ == '__main__':
    # --- Initialize test variables ---
    top_coins_cmc = get_top_50_coins_cmc()
    
    # Default test coin values (used if fetching top_coins_cmc fails or is empty)
    test_coin_symbol = "BTC"
    test_coin_name = "Bitcoin"
    second_test_coin_name = "Ethereum"
    second_test_coin_symbol = "ETH" # For testing aggregation by name which might need symbol lookup

    if top_coins_cmc and len(top_coins_cmc) > 0:
        test_coin_symbol = top_coins_cmc[0]['symbol']
        test_coin_name = top_coins_cmc[0]['name']
        if len(top_coins_cmc) > 1:
            second_test_coin_name = top_coins_cmc[1]['name']
            second_test_coin_symbol = top_coins_cmc[1]['symbol']
    else:
        print("Warning: Could not fetch top coins list from CMC. Using default test values.")

    # --- Test CoinMarketCap Individual Functions ---
    print("\n" + "="*15 + " Testing CoinMarketCap Individual Functions " + "="*15)
    if top_coins_cmc:
        print(f"Successfully fetched {len(top_coins_cmc)} coins from CMC.")
        print("Top 3 coins from CMC:")
        for i, coin in enumerate(top_coins_cmc[:3]):
            print(f"  {i+1}. {coin['name']} ({coin['symbol']}): Rank {coin['rank']}, Price ${coin.get('price_usd', 0):.2f}")
    
    print(f"\nFetching details for {test_coin_name} ({test_coin_symbol}) from CMC...")
    coin_details_cmc = get_coin_data_cmc(coin_symbol=test_coin_symbol)
    if coin_details_cmc:
        print(f"  Price: ${coin_details_cmc.get('price_usd', 0):.2f}, Market Cap: ${coin_details_cmc.get('market_cap_usd', 0):.0f}")
    else:
        print(f"  Failed to fetch details for {test_coin_symbol}.")
    
    # --- Test Newsdata.io Individual Function ---
    print("\n" + "="*15 + " Testing Newsdata.io Individual Function " + "="*15)
    if not NEWSDATA_API_KEY:
        print("Skipping Newsdata.io tests as API key is not configured.")
    else:
        print(f"\nFetching news for '{test_coin_name}' from Newsdata.io...")
        news_articles_test = get_newsdata_io_news(coin_name=test_coin_name, size=3)
        if news_articles_test is not None: # Check for None to indicate potential API key issues etc.
            if news_articles_test: # Check if list is non-empty
                print(f"Found {len(news_articles_test)} news articles for {test_coin_name}:")
                for i, article in enumerate(news_articles_test):
                    print(f"  {i+1}. {article['title']} (Source: {article.get('source_id', 'N/A')})")
            else:
                print(f"No news articles found for {test_coin_name} on Newsdata.io.")
        else:
            print(f"Failed to fetch news for {test_coin_name} from Newsdata.io (check API key or error messages).")

    # --- Test Data Aggregation Function ---
    print("\n" + "="*20 + " Testing Data Aggregation " + "="*20)
    
    # Test 1: Using a known symbol (e.g., BTC)
    print(f"\n--- Aggregating for '{test_coin_symbol}' (Symbol) ---")
    aggregated_data_sym = get_aggregated_coin_data(coin_identifier=test_coin_symbol)
    if aggregated_data_sym:
        print(f"\n--- Formatted Aggregated Data for '{aggregated_data_sym.get('resolved_name_for_news', test_coin_symbol)}' ---")
        if aggregated_data_sym["market_data"]:
            md = aggregated_data_sym["market_data"]
            print(f"  Market Data: Name: {md.get('name', 'N/A')}, Symbol: {md.get('symbol', 'N/A')}, Price: ${md.get('price_usd', 0):.2f}, Rank: {md.get('rank', 'N/A')}")
        else:
            print(f"  No market data found for '{test_coin_symbol}'.")
        
        print(f"  News Articles ({len(aggregated_data_sym['news_articles'])} found):")
        for i, news in enumerate(aggregated_data_sym['news_articles'][:3]): # Show first 3 news
            print(f"    {i+1}. {news.get('title', 'No Title')}")
        if not aggregated_data_sym['news_articles']:
            print("    No news articles found.")
    else:
        print(f"Failed to aggregate any data for '{test_coin_symbol}'.")

    # Test 2: Using a known name (e.g., Ethereum)
    # get_aggregated_coin_data will try to use "Ethereum" as a symbol for CMC, which might fail.
    # News should work with the name "Ethereum".
    print(f"\n--- Aggregating for '{second_test_coin_name}' (Name) ---")
    aggregated_data_name = get_aggregated_coin_data(coin_identifier=second_test_coin_name)
    if aggregated_data_name:
        print(f"\n--- Formatted Aggregated Data for '{aggregated_data_name.get('resolved_name_for_news', second_test_coin_name)}' ---")
        if aggregated_data_name["market_data"]: # This might be None if name isn't a recognized symbol by CMC
            md = aggregated_data_name["market_data"]
            print(f"  Market Data: Name: {md.get('name', 'N/A')}, Symbol: {md.get('symbol', 'N/A')}, Price: ${md.get('price_usd', 0):.2f}, Rank: {md.get('rank', 'N/A')}")
        else:
            print(f"  No market data found for '{second_test_coin_name}' when used as a symbol for CMC (this might be expected).")
        
        print(f"  News Articles ({len(aggregated_data_name['news_articles'])} found):")
        for i, news in enumerate(aggregated_data_name['news_articles'][:3]):
            print(f"    {i+1}. {news.get('title', 'No Title')}")
        if not aggregated_data_name['news_articles']:
            print("    No news articles found.")
    else:
        print(f"Failed to aggregate any data for '{second_test_coin_name}'.")

    # Test 3: Non-existent coin
    print("\n--- Aggregating for 'NonExistentCoinXYZ123' ---")
    aggregated_non_existent = get_aggregated_coin_data(coin_identifier="NonExistentCoinXYZ123")
    if not aggregated_non_existent:
        print("Correctly handled aggregation for a non-existent coin (returned None).")
    elif not aggregated_non_existent.get("market_data") and not aggregated_non_existent.get("news_articles"):
         print("Correctly handled aggregation for a non-existent coin (no data found in dict).")
    else:
        # This case should ideally not be hit if the above two cover it.
        print("Aggregation for non-existent coin did not behave as expected, some data might have been found:", aggregated_non_existent)
