# main.py
import string

from services.aggregator import get_aggregated_coin_data
from services.market_data import get_top_50_coins_cmc
from ai_processor import generate_crypto_assistant_response

# --- Helper function to extract coin identifier ---
def extract_coin_identifier_from_query(query):
    """
    Simpler extraction of a potential coin identifier (word or symbol) from the user query.
    Focuses on capitalized words or uppercase sequences.
    """
    query = query.translate(str.maketrans('', '', string.punctuation))
    words = query.split()
    
    # Try to find a sequence of capitalized words (potential multi-word name)
    # or a single capitalized word.
    # Also look for all-caps words (potential symbols).
    
    # First pass for explicit symbols (all caps, short)
    for word in words:
        if word.isupper() and 1 < len(word) < 7: # e.g., BTC, ETH, SOL, DOGE
            return word # Return the first clear symbol found

    # Second pass for capitalized words / potential names
    # We try to reconstruct multi-word names like "Shiba Inu"
    # This is still very basic.
    current_name_parts = []
    longest_potential_name = ""

    for word in words:
        # Ignore common lowercase words that might be part of a query but not a coin name
        if word.islower() and word not in ['of', 'the', 'for', 'and', 'about', 'price', 'news', 'market', 'cap', 'tell', 'me', 'what', "what's", 'is', 'latest', 'current']:
            if current_name_parts: # if we were building a name, stop
                name_candidate = " ".join(current_name_parts)
                if len(name_candidate) > len(longest_potential_name):
                    longest_potential_name = name_candidate
                current_name_parts = []
            continue # Skip this lowercase word

        if word.istitle() or word.isupper(): # istitle() checks for "Titlecase"
            current_name_parts.append(word)
        elif current_name_parts: # Word is not title/upper, and we were building a name
            name_candidate = " ".join(current_name_parts)
            if len(name_candidate) > len(longest_potential_name):
                longest_potential_name = name_candidate
            current_name_parts = [] # Reset

    # Check after loop if current_name_parts still has something
    if current_name_parts:
        name_candidate = " ".join(current_name_parts)
        if len(name_candidate) > len(longest_potential_name):
            longest_potential_name = name_candidate
            
    if longest_potential_name:
        return longest_potential_name

    # Fallback for common lowercase names if no capitalized/uppercase found
    query_lower = query.lower()
    common_names_map = {
        "bitcoin": "Bitcoin",
        "btc": "Bitcoin",
        "ethereum": "Ethereum",
        "eth": "Ethereum",
        "solana": "Solana",
        "sol": "Solana",
        "ripple": "XRP",
        "xrp": "XRP",
        "cardano": "Cardano",
        "ada": "Cardano",
        "dogecoin": "Dogecoin",
        "doge": "Dogecoin",
        "shiba inu": "Shiba Inu",
        "shib": "Shiba Inu",
        "binance coin": "BNB",
        "bnb": "BNB",
        "avalanche": "Avalanche",
        "avax": "Avalanche",
        "polkadot": "Polkadot",
        "dot": "Polkadot",
        "tron": "TRON",
        "trx": "TRON",
        "chainlink": "Chainlink",
        "link": "Chainlink",
        "polygon": "Polygon",
        "matic": "Polygon",
        "litecoin": "Litecoin",
        "ltc": "Litecoin",
        "uniswap": "Uniswap",
        "uni": "Uniswap",
        "stellar": "Stellar",
        "xlm": "Stellar",
        "aptos": "Aptos",
        "apt": "Aptos",
        "arbitrum": "Arbitrum",
        "arb": "Arbitrum",
        "internet computer": "Internet Computer",
        "icp": "Internet Computer",
        "vechain": "VeChain",
        "vet": "VeChain"
}

    for lc_name, canonical_form in common_names_map.items():
        if lc_name in query_lower:
            return canonical_form
            
    return None


def main():
    print("Welcome to the AI Crypto Assistant!")
    print("You can ask questions like: 'What's the latest news about Ethereum?' or 'Tell me about Bitcoin price.'")
    print("Type 'top50' to see the list of top 50 coins by market cap.")
    print("Type 'quit' or 'exit' to leave.")

    # Fetch top 50 coins once at the start for better coin identification
    print("\nFetching initial coin list...")
    top_50_coins_list = get_top_50_coins_cmc()
    if top_50_coins_list:
        print(f"Fetched {len(top_50_coins_list)} coins for reference.")
        # Prepare a list of dicts with 'name', 'symbol', 'id' for easier lookup
        known_coin_refs_for_resolution = [
            {'name': c['name'], 'symbol': c['symbol'], 'id': c.get('id')} 
            for c in top_50_coins_list
        ]
    else:
        print("Could not fetch the top 50 coins list. Coin identification might be less accurate.")
        known_coin_refs_for_resolution = []


    while True:
        user_query = input("\nAsk me about crypto (or type 'quit'): ").strip()

        if not user_query:
            continue
        if user_query.lower() in ['quit', 'exit']:
            print("Goodbye!")
            break
        
        if user_query.lower() == 'top50':
            if top_50_coins_list:
                print("\n--- Top 50 Coins by Market Cap ---")
                for i, coin in enumerate(top_50_coins_list):
                    price_val = coin.get('price_usd')
                    price_str = f"${price_val:.2f}" if isinstance(price_val, (int, float)) else str(price_val)
                    print(f"{i+1}. {coin.get('name', 'N/A')} ({coin.get('symbol', 'N/A')}) - Price: {price_str}")
            else:
                print("Sorry, I couldn't retrieve the top 50 coins list at this moment.")
            continue

        # --- Step 1: Extract potential coin term from query ---
        extracted_term = extract_coin_identifier_from_query(user_query)

        if not extracted_term:
            print("I couldn't identify a specific cryptocurrency in your query. Please try rephrasing, e.g., 'Tell me about Bitcoin'.")
            # Optionally, send the generic query to the AI without specific data
            # generic_response = generate_crypto_assistant_response(user_query, {"market_data": None, "news_articles": []})
            # print(f"\nAI Assistant (General): {generic_response}")
            continue
        
        print(f"\nExtracted term: '{extracted_term}'. Attempting to resolve...")

        # --- Step 2: Resolve extracted term to a canonical coin (symbol) ---
        target_symbol_for_api = None
        resolved_coin_name = extracted_term # Default name for news if not resolved better
        
        # Try to match extracted_term (as name or symbol) with our known_coin_refs_for_resolution
        for coin_detail in known_coin_refs_for_resolution:
            # Check symbol match first (more precise)
            if extracted_term.upper() == coin_detail['symbol'].upper():
                target_symbol_for_api = coin_detail['symbol'] 
                resolved_coin_name = coin_detail['name']
                print(f"Resolved '{extracted_term}' to official symbol: {target_symbol_for_api} ({resolved_coin_name})")
                break
            # Then check name match
            if extracted_term.lower() == coin_detail['name'].lower():
                target_symbol_for_api = coin_detail['symbol']
                resolved_coin_name = coin_detail['name']
                print(f"Resolved '{extracted_term}' to official symbol: {target_symbol_for_api} ({resolved_coin_name}) from name match.")
                break
        
        if not target_symbol_for_api:
            # If not resolved from top 50, use the extracted_term.
            # If it looks like a symbol (all caps, short), pass it as is.
            # If it looks like a name, get_aggregated_coin_data will .upper() it for CMC symbol attempt.
            if extracted_term.isupper() and 1 < len(extracted_term) < 7:
                target_symbol_for_api = extracted_term
                resolved_coin_name = extracted_term # News will use this if CMC doesn't return a name
                print(f"Could not resolve '{extracted_term}' in top 50. Using '{target_symbol_for_api}' as a potential symbol directly.")
            else:
                target_symbol_for_api = extracted_term 
                resolved_coin_name = extracted_term # This name will be used for news directly
                print(f"Could not resolve '{extracted_term}' in top 50 or as a clear symbol. Passing '{target_symbol_for_api}' for aggregation.")
        
        # The `get_aggregated_coin_data` function is designed to take a coin_identifier.
        # If it's a symbol, it uses it. If it's a name, it tries .upper() for CMC symbol
        # and the original name for news. Our `target_symbol_for_api` now aims to be
        # the best candidate (preferably a resolved symbol) for this.
        print(f"Okay, looking for information using API target: '{target_symbol_for_api}'...")
        
        aggregated_data = get_aggregated_coin_data(target_symbol_for_api)

        # --- Step 3: Handle Aggregated Data and Generate AI Response ---
        if not aggregated_data:
            print(f"Sorry, I couldn't retrieve any information for '{target_symbol_for_api}'. It might be an unsupported coin or there was an issue fetching data.")
            # Let AI try to respond based on the query and lack of specific data
            ai_response = generate_crypto_assistant_response(user_query, 
                                                             {"query_identifier": target_symbol_for_api, 
                                                              "resolved_name_for_news": resolved_coin_name, # Give context
                                                              "market_data": None, 
                                                              "news_articles": []})
            print(f"\nAI Assistant: {ai_response}")
            continue
        
        # If aggregated_data exists but is essentially empty
        if not aggregated_data.get("market_data") and not aggregated_data.get("news_articles"):
             print(f"I found no specific market data or news for '{target_symbol_for_api}'.")
             # Still, let the AI try to formulate a response based on this lack of data
             # Pass the resolved_coin_name to the AI in this case too.
             if "resolved_name_for_news" not in aggregated_data: # Ensure it's there
                 aggregated_data["resolved_name_for_news"] = resolved_coin_name
             ai_response = generate_crypto_assistant_response(user_query, aggregated_data)
             print(f"\nAI Assistant: {ai_response}")
             continue

        # Ensure resolved_name_for_news is in aggregated_data if market_data was missing
        # but news was found using the initially resolved_coin_name.
        if not aggregated_data.get("market_data") and "resolved_name_for_news" not in aggregated_data.get("news_articles", {}):
            # This case is tricky; get_aggregated_coin_data sets 'resolved_name_for_news'
            # based on market_data if found, or the input identifier.
            # We want the AI to know what name was used for the news part if market data failed.
            # Let's ensure our prompt in ai_processor handles this.
            # The `aggregated_data` from `get_aggregated_coin_data` already includes
            # 'query_identifier' and 'resolved_name_for_news' based on its internal logic.
            pass # The current structure of aggregated_data should be sufficient for ai_processor

        print("Asking the AI...")
        ai_response = generate_crypto_assistant_response(user_query, aggregated_data)

        # --- Step 4: Display Response ---
        print(f"\nAI Assistant:")
        print(ai_response)

if __name__ == "__main__":
    main()