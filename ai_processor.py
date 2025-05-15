# ai_processor.py
import google.generativeai as genai
import json # For formatting data in the prompt

from config import GEMINI_API_KEY
from services.news_service import get_newsdata_io_news

def configure_gemini():
    """Configures the Gemini API with the API key."""
    if not GEMINI_API_KEY:
        print("Error: GEMINI_API_KEY not found in config. Exiting AI processing.")
        return None
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash')
        return model
    except Exception as e:
        print(f"Error configuring Gemini or initializing model: {e}")
        return None

def generate_crypto_assistant_response(user_query, aggregated_data):
    """
    Generates a response to a user's query using Gemini, based on aggregated crypto data.

    :param user_query: The original question from the user (e.g., "What's the latest on Bitcoin?").
    :param aggregated_data: A dictionary containing 'market_data' and 'news_articles'.
    :return: A string containing the AI's response, or an error message.
    """
    model = configure_gemini()
    if not model:
        return "Sorry, I couldn't connect to the AI model at the moment."

    # --- Construct the prompt for Gemini ---
    prompt_parts = []
    prompt_parts.append(f"You are an AI Crypto Assistant. Answer the user's question based on the provided data. Be concise and informative.")
    prompt_parts.append(f"\nUser Query: \"{user_query}\"")

    prompt_parts.append("\n--- Provided Data ---")

    # Add Market Data to Prompt
    if aggregated_data.get("market_data"):
        market_info = aggregated_data["market_data"]
        prompt_parts.append("\nMarket Data:")
        # Safely get name and symbol, defaulting if not present
        name = market_info.get('name', aggregated_data.get('query_identifier', 'the queried coin'))
        symbol = market_info.get('symbol', 'N/A')
        price = market_info.get('price_usd', 'N/A')
        market_cap = market_info.get('market_cap_usd', 'N/A')
        rank = market_info.get('rank', 'N/A')
        change_24h = market_info.get('percent_change_24h', 'N/A')

        prompt_parts.append(f"  - Name: {name} ({symbol})")
        prompt_parts.append(f"  - Current Price: ${price:.2f}" if isinstance(price, (int, float)) else f"  - Current Price: {price}")
        prompt_parts.append(f"  - Market Cap: ${market_cap:,.0f}" if isinstance(market_cap, (int, float)) else f"  - Market Cap: {market_cap}")
        prompt_parts.append(f"  - Rank: {rank}")
        prompt_parts.append(f"  - 24h Change: {change_24h:.2f}%" if isinstance(change_24h, (int, float)) else f"  - 24h Change: {change_24h}")
        prompt_parts.append(f"  - Last Updated: {market_info.get('last_updated', 'N/A')}")
    else:
        prompt_parts.append(f"\nNo specific market data was found for '{aggregated_data.get('query_identifier', 'the coin')}'.")

    # Add News Headlines to Prompt
    if aggregated_data.get("news_articles"):
        news_items = aggregated_data["news_articles"]
        prompt_parts.append("\nRecent News Headlines:")
        if news_items:
            for i, article in enumerate(news_items[:5]): # Show top 5 news
                prompt_parts.append(f"  {i+1}. {article.get('title', 'N/A')} (Source: {article.get('source_id', 'N/A')})")
        else:
            prompt_parts.append("  No recent news articles found.")
    else:
        prompt_parts.append("\nNo news data was available.")

    prompt_parts.append("\n--- End of Provided Data ---")
    prompt_parts.append("\nBased on this data, please answer the user's query. If the data is insufficient to directly answer, state that.")
    
    full_prompt = "\n".join(prompt_parts)

    try:
        response = model.generate_content(full_prompt)
        
        # Handle cases where the response might not have text or parts
        if response.parts:
            return response.text
        elif hasattr(response, 'text'): # Check if .text attribute exists directly
            return response.text
        else:
            # Investigate the response structure if this happens.
            # print("Gemini response structure:", response)
            # This part is to try and extract text if the primary methods fail.
            # It attempts to handle different possible response structures.
            try:
                # Check if response.candidates[0].content.parts[0].text exists
                if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
                    return response.candidates[0].content.parts[0].text
            except (IndexError, AttributeError) as e:
                print(f"Could not extract text from Gemini response (candidates): {e}")
            return "Sorry, I received an empty or unparseable response from the AI."

    except Exception as e:
        print(f"Error during Gemini API call: {e}")
        # You might want to inspect response.prompt_feedback if available
        if hasattr(response, 'prompt_feedback'):
             print(f"Prompt Feedback: {response.prompt_feedback}")
        return f"Sorry, I encountered an error while generating the response: {e}"
    

def filter_news_by_coin(news_list, coin_name):
    coin_name_lower = coin_name.lower()
    filtered = []
    for article in news_list:
        title = article.get('title')
        desc = article.get('description')

        # Безопасно приводим к строке и к нижнему регистру
        title_text = title.lower() if isinstance(title, str) else ""
        desc_text = desc.lower() if isinstance(desc, str) else ""

        if coin_name_lower in title_text or coin_name_lower in desc_text:
            filtered.append(article)
    return filtered


def generate_news(coin_name):
    model = configure_gemini()
    if not model:
        return "Sorry, I couldn't connect to the AI model at the moment."

    news = get_newsdata_io_news(coin_name)
    news = filter_news_by_coin(news, coin_name)
    if not news:
        return "No news found specifically related to this coin."

    news_text = ""
    for i, article in enumerate(news):
        title = article.get('title', 'No title')
        desc = article.get('description', 'No description')
        link = article.get('link', '')
        news_text += f"{i+1}. {title}\n{desc}\nLink: {link}\n\n"

    prompt = (
        "You are an expert crypto analyst.\n"
        "Summarize each news article briefly, then provide at least 200 words detailed explanation per article.\n"
        "Include the link at the end of each summary.\n"
        f"Here are the news articles:\n\n{news_text}"
    )

    try:
        response = None
        response = model.generate_content(prompt)
        if hasattr(response, 'parts') and response.parts:
            return response.parts[0].text
        elif hasattr(response, 'text'):
            return response.text
        else:
            if (hasattr(response, 'candidates') and response.candidates
                and hasattr(response.candidates[0], 'content')
                and hasattr(response.candidates[0].content, 'parts')
                and response.candidates[0].content.parts):
                return response.candidates[0].content.parts[0].text
            else:
                return "Sorry, I received an empty or unparseable response from the AI."
    except Exception as e:
        print(f"Error during Gemini API call: {e}")
        return f"Sorry, I encountered an error while generating the response: {e}"
