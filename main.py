import time
import asyncio
import os
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

    sia_previous_posts = sia_memory.get_posts()
    print("Posts from memory:\n")
    for post in sia_previous_posts[-20:]:
        print(post[4])
        print("\n\n")
    print(f"{'*'*100}\n\n")


    # wait between 30 and 60 minutes
    #   before generating and publishing the next tweet
    times_of_day = sia.times_of_day()
    wait_time = random.randint(1800, 3600)
    wait_hours = wait_time // 3600
    wait_minutes = (wait_time % 3600) // 60
    wait_seconds = wait_time % 60
    print(f"\n\nWaiting for {wait_hours} hours, {wait_minutes} minutes, and {wait_seconds} seconds before generating and publishing next tweet.\n\n")
    time.sleep(wait_time)


    # for now, for testing purposes we generate a tweet
    #   using a random time of day as context for AI,
    #   ignoring the actual time of the day
    time_of_day = random.choice(times_of_day)
    post, media = sia.generate_post(time_of_day=time_of_day)
    sia_twitter.publish_post(post, [media])
    sia.memory.add_post(platform="twitter", account=character_name, content=post)


    print(f"New tweet generated, added to memory and published:\n")
    print(post)
    print("\n\n")



# Start the asyncio event loop
if __name__ == '__main__':
    asyncio.run(main())
