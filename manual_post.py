"""

This is a temporary solution to post a tweet manually
the way it will be added to the list to be tracked and respond to replies.
As of 2024.12.04, if posting manually on Twitter itself, Sia won't see this post and thus replies to it.
This script is a useful way to post developer updates or other important messages.

"""


import asyncio
import os

from dotenv import load_dotenv
load_dotenv()

from sia.sia import Sia
from sia.modules.knowledge.GoogleNews.google_news import GoogleNewsModule
from sia.memory.schemas import SiaMessageGeneratedSchema

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
        knowledge_module_classes=[GoogleNewsModule],
        logging_enabled=logging_enabled
    )

    character_name = sia.character.name
    

    # posting
    #   a new tweet
    
    post_text = """
        Developer update:

        - Sia framework got its first documentation. Any developer can create and deploy a Sia agent within 30 minutes!

        - Modules and plugins are now available in Sia.
        The first one - Google News.
        With this module, Sia can collect relevant news daily and write posts based on them (LatestNews plugin)!
    """.replace("        ", "")
    
    post = SiaMessageGeneratedSchema(
        platform="twitter",
        author=sia.character.twitter_username,
        character=character_name,
        content=post_text
    )
    
    media = []
    
    tweet_id = sia.twitter.publish_post(post, media)

    if tweet_id and tweet_id is not Forbidden:
        sia.memory.add_message(post, tweet_id)



# Start the asyncio event loop
if __name__ == '__main__':
    asyncio.run(main())
