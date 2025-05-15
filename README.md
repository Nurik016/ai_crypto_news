# Ai_crypto_news

---
A project for collecting, analyzing, and displaying cryptocurrency news, with interaction via CLI or a Telegram bot.
---

## Installation and Setup

---
Follow these steps to set up and run the project:
---

1.  **Clone the repository:**
    Open your terminal or command prompt and execute the command:
    ```bash
    git clone https://github.com/Nurik016/ai_crypto_news
    ```

2.  **Navigate to the project directory:**
    ```bash
    cd ai_crypto_news
    ```

3.  **Create a virtual environment:**
    This helps to isolate project dependencies.

    *   **Windows:**
        ```bash
        python -m venv venv
        ```
        or
        ```bash
        py -m venv venv
        ```

    *   **macOS / Linux:**
        ```bash
        python3 -m venv venv
        ```

4.  **Activate the virtual environment:**

    *   **Windows (Command Prompt/PowerShell):**
        ```bash
        venv\Scripts\activate
        ```

    *   **macOS / Linux (bash/zsh):**
        ```bash
        source venv/bin/activate
        ```

    ** After activation, you should see `(venv)` at the beginning of your command prompt.

6.  **Install the required libraries:**
    Ensure your virtual environment is activated, then run:
    ```bash
    pip install -r requirements.txt
    ```
    **If `pip` doesn't work, try `pip3`.**

7.  **Create a `.env` file for API keys:**
    In the root directory of the project, create a file named `.env`. Copy the following template into it and replace `YOUR_KEY` with your actual API keys:

    ```dotenv
    NEWSDATA_API_KEY=YOUR_NEWSDATA_API_KEY
    COINMARKETCAP_API_KEY=YOUR_COINMARKETCAP_API_KEY
    GEMINI_API_KEY=YOUR_GEMINI_API_KEY
    BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
    ```
    *   `NEWSDATA_API_KEY`:
        Key for the NewsData.io service.
    *   `COINMARKETCAP_API_KEY`:
        Key for the CoinMarketCap API.
    *   `GEMINI_API_KEY`:
        Key for the Gemini API (if used).
    *   `BOT_TOKEN`:
        Your Telegram bot token (required to run `bot.py`).

## Usage

---
**Running the CLI version:**
To run the Command Line Interface (CLI) version, execute:
---
```bash
python3 main.py
```

Or, if python3 is not your primary alias, use python main.py (assuming you are in a virtual environment with Python 3.x).

**Running the Telegram bot:**

Ensure you have added your BOT_TOKEN to the .env file.

Run the bot with the command:
```bash
python3 bot.py
```

## 💻 Demo Screenshots
![](https://iimg.su/s/15/p9vy74noOfTQjCWRcbgM32n5JAeVUN6zcrIDTEox.png)
![](https://iimg.su/s/15/zfc5EIfH4YAC19VOM3xLKZGjuWDcbZeqkWOKCtAQ.png)
![](https://iimg.su/s/15/oU5qvdUwsAgiEONG9aVM1T3kGEgzPwDSa38bmYau.png)


## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
