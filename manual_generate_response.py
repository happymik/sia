"""


"""


import asyncio
import os
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

from sia.sia import Sia
from sia.modules.knowledge.GoogleNews.google_news import GoogleNewsModule
from sia.memory.schemas import SiaMessageSchema, SiaMessageGeneratedSchema

from tweepy import Forbidden

from utils.logging_utils import setup_logging, log_message, enable_logging

logger = setup_logging()
logging_enabled = True
enable_logging(logging_enabled)



async def main():
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
        logging_enabled=logging_enabled
    )

    character_name = sia.character.name
    
    
    tweet_to_respond_text = """
    """
    
    
    message = SiaMessageSchema(
        conversation_id = None,
        content = tweet_to_respond_text,
        platform = "twitter",
        author = "Paradigmus",
        character = character_name,
        response_to = None,
        flagged = False,
        message_metadata = {},
        wen_posted = datetime.now(),
        original_data = {}
    )
    
    response = sia.generate_response(message=message)# -> SiaMessageGeneratedSchema|None:
    
    



# Start the asyncio event loop
if __name__ == '__main__':
    asyncio.run(main())
