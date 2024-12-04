import os
from dotenv import load_dotenv
load_dotenv()

from sia.sia import Sia
from sia.clients.telegram.telegram_client import SiaTelegram


def main():
    character_name_id = os.getenv("CHARACTER_NAME_ID")

    sia = Sia(
        character_json_filepath=f"characters/{character_name_id}.json",
        twitter_creds = {
            "api_key": os.getenv("TW_API_KEY"),
            "api_secret_key": os.getenv("TW_API_KEY_SECRET"),
            "access_token": os.getenv("TW_ACCESS_TOKEN"),
            "access_token_secret": os.getenv("TW_ACCESS_TOKEN_SECRET"),
            "bearer_token": os.getenv("TW_BEARER_TOKEN")
        },
        memory_db_path=os.getenv("DB_PATH"),
        # knowledge_module_classes=[GoogleNewsModule],
        # logging_enabled=logging_enabled
    )

    bot = SiaTelegram(tg_bot_token=os.getenv("TG_BOT_TOKEN"), chat_id='-1002312730638', sia=sia)
    bot.run()

if __name__ == '__main__':
    main()
