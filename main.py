
import time
import asyncio
import os
import json
import random

from dotenv import load_dotenv
load_dotenv()

from sia.sia import Sia
from sia.character import Character
from sia.memory.memory import SiaMemory
# from sia.clients.telegram.telegram_client import SiaTelegram
from sia.clients.twitter.twitter_official_api_client import SiaTwitterOfficial


async def main():
    
    character_name = os.getenv("CHARACTER_NAME")
    sia_character = Character(json_file=f"characters/{character_name}.json")

    sia_memory = SiaMemory(character=character_name)
    # sia_memory.clear_posts() # to clear all posts from memory

    sia = Sia(character=sia_character, memory=sia_memory, logging_enabled=False)

    sia_twitter = SiaTwitterOfficial(
        api_key=os.getenv("TW_API_KEY"),
        api_secret_key=os.getenv("TW_API_KEY_SECRET"),
        access_token=os.getenv("TW_ACCESS_TOKEN"),
        access_token_secret=os.getenv("TW_ACCESS_TOKEN_SECRET")
    )

    # sia_client = SiaTelegram(bot_token=os.getenv("TG_BOT_TOKEN"), chat_id="@real_sia")

    times_of_day = sia.times_of_day()
    sia_previous_posts = sia_memory.get_posts()

    print("Posts from memory:\n")
    for post in sia_previous_posts[-20:]:
        print(post[4])
        print("\n\n")
    print(f"{'*'*100}\n\n")


    while True:
        
        # for now, for testing purposes we publish a tweet for each time of day one by one, ignoring the actual time of the day
        for time_of_day in times_of_day:
            post = sia.generate_post(time_of_day=time_of_day)

            sia_twitter.publish_post(post)
            # await sia_client.publish_post(post)

            sia.memory.add_post(platform="twitter", account=character_name, content=post)

            print(f"New tweet generated, added to memory and published:\n")
            print(post)
            print("\n\n")

            # wait between 90 and 120 minutes before generating and publishing the next tweet
            time.sleep(random.randint(5400, 7200))


asyncio.run(main())

