import asyncio  
import os  
import logging  
  
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message  
from aiogram.filters import CommandStart  
from dotenv import load_dotenv
from main import generate_crypto_assistant_response, extract_coin_identifier_from_query
from services.aggregator import get_aggregated_coin_data
from services.market_data import get_top_50_coins_cmc

  
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
  
bot = Bot(token=TOKEN)  
dp = Dispatcher()  
  
@dp.message(CommandStart())  
async def start(message: Message):  
    # kb = InlineKeyboardMarkup(inline_keyboard=[
    #     InlineKeyboardButton(text='Top50', callback_data='top50'),
    # ])
    await message.answer("Hello, I am Crypto Assistant Bot, You can ask me about top 50 coins, and other questions about crypto")  

@dp.message(F.text.lower() == 'top50')
async def top50_coins(message: Message):
    top50 = get_top_50_coins_cmc()
    if top50:
            response_text = "\n".join(
                f"{i+1}. {coin['name']} ({coin['symbol']}) - Price: ${coin['price_usd']:.2f}"
                for i, coin in enumerate(top50)
            )
    else:
            response_text = "Sorry, I couldn't fetch the top 50 coins right now."
    await message.answer(response_text)

@dp.message()
async def request_bot(message: Message):
    user_text = message.text.strip()
    coin_identifier = extract_coin_identifier_from_query(user_text)
    if not coin_identifier:
        await message.answer("I couldn't identify a cryptocurrency in your query. Please try again.")
        return

    aggregated_data = get_aggregated_coin_data(coin_identifier)
    if aggregated_data is None:
        aggregated_data = {
            "query_identifier": coin_identifier,
            "resolved_name_for_news": coin_identifier,
            "market_data": None,
            "news_articles": []
        }
    response = generate_crypto_assistant_response(user_text, aggregated_data)
    await message.answer(response)


    
async def main():  
    # Тем самым, сообщения, которые были отправлены боту, когда он был выключен, при включении будут игнорироваться
    await bot.delete_webhook(drop_pending_updates=True)  
    await dp.start_polling(bot)  
  
if __name__ == '__main__':  
    logging.basicConfig(level=logging.INFO)  
    print("Running bot...")  
    try:  
        asyncio.run(main())  
    except KeyboardInterrupt:  
        print("Exit")