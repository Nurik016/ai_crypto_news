# market_data.py
import requests
import json

from config import COINMARKETCAP_API_KEY, COINMARKETCAP_API_URL

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
