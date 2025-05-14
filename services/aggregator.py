# aggregator.py
from services.news_service import get_newsdata_io_news
from services.market_data import get_coin_data_cmc

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