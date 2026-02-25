import os
from dotenv import load_dotenv
from src.telegram_bot import TGNotificationBot

def main():
    # Load environment variables from .env file
    load_dotenv()

    # Get credentials
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    interval_str = os.getenv("SCAN_INTERVAL", "240")
    try:
        scan_interval = int(interval_str)
    except ValueError:
        scan_interval = 240

    if not telegram_token or telegram_token == "your_telegram_bot_token_here":
        print("Please set your TELEGRAM_BOT_TOKEN in the .env file.")
        return
        
    if not telegram_chat_id or telegram_chat_id == "your_telegram_chat_id_here":
        print("Please set your TELEGRAM_CHAT_ID in the .env file.")
        return

    # Initialize and run the bot
    bot = TGNotificationBot(token=telegram_token, chat_id=telegram_chat_id)
    bot.run(default_interval_minutes=scan_interval)

if __name__ == "__main__":
    main()
