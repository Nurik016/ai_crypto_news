import asyncio  
import os  
import logging  
  
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message  
from aiogram.filters import CommandStart, Command, CommandObject
from dotenv import load_dotenv
from main import generate_crypto_assistant_response, extract_coin_identifier_from_query
from services.aggregator import get_aggregated_coin_data
from services.market_data import get_top_50_coins_cmc
from ai_processor import generate_news

  
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
  
bot = Bot(token=TOKEN)  
dp = Dispatcher()  
  
@dp.message(CommandStart())  
async def start(message: Message):  
    # kb = InlineKeyboardMarkup(inline_keyboard=[
    #     InlineKeyboardButton(text='Top50', callback_data='top50'),
    # ])
    await message.answer("Hello, I am Crypto Assistant Bot, You can ask me about top 50 coins, and about crypto symbols")  

MAX_MESSAGE_LENGTH = 4096

def split_message(text):
    # Разбивает длинный текст по 4096 символов, стараясь не резать посреди слов
    chunks = []
    while len(text) > MAX_MESSAGE_LENGTH:
        split_index = text.rfind('\n', 0, MAX_MESSAGE_LENGTH)
        if split_index == -1:
            split_index = MAX_MESSAGE_LENGTH
        chunks.append(text[:split_index])
        text = text[split_index:]
    chunks.append(text)
    return chunks

@dp.message(F.text.func(lambda text: text and text.replace(" ", "").lower() == 'top50'))
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
    user_text = message.text.strip().lower()

    # Проверяем, содержит ли сообщение "news" или "новости"
    if "news" in user_text or "новости" in user_text:
        coin_identifier = extract_coin_identifier_from_query(message.text)
        if not coin_identifier:
            await message.answer("Не удалось распознать название монеты для новостей.")
            return
        
        coin_identifier = (coin_identifier or "").replace(" ", "").lower()
        loop = asyncio.get_event_loop()
        news_text = await loop.run_in_executor(None, generate_news, coin_identifier)

        chunks = split_message(news_text)
        for chunk in chunks:
            await message.reply(chunk)
        return

    # Если нет ключевых слов, продолжаем с обычным ответом AI
    coin_identifier = extract_coin_identifier_from_query(message.text)
    if not coin_identifier:
        await message.answer("Я не смог определить криптовалюту в вашем запросе. Пожалуйста, попробуйте ещё раз.")
        return

    aggregated_data = get_aggregated_coin_data(coin_identifier)
    if aggregated_data is None:
        aggregated_data = {
            "query_identifier": coin_identifier,
            "resolved_name_for_news": coin_identifier,
            "market_data": None,
            "news_articles": []
        }

    response = generate_crypto_assistant_response(message.text, aggregated_data)
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
