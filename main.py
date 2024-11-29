import time
import asyncio
import os
import random

from dotenv import load_dotenv
load_dotenv()

from sia.sia import Sia
from sia.character import SiaCharacter
from sia.memory.memory import SiaMemory
# from sia.clients.telegram.telegram_client import SiaTelegram
from sia.clients.twitter.twitter_official_api_client import SiaTwitterOfficial

from tweepy import Forbidden


async def main():
    character_name = os.getenv("CHARACTER_NAME").capitalize()

    sia = Sia(
        character=SiaCharacter(json_file=f"characters/{character_name}.json"),
        twitter=SiaTwitterOfficial(
            api_key=os.getenv("TW_API_KEY"),
            api_secret_key=os.getenv("TW_API_KEY_SECRET"),
            access_token=os.getenv("TW_ACCESS_TOKEN"),
            access_token_secret=os.getenv("TW_ACCESS_TOKEN_SECRET"),
            bearer_token=os.getenv("TW_BEARER_TOKEN")
        ),
        logging_enabled=True
    )
    
    my_tweet_ids = sia.twitter.get_my_tweet_ids()
    print(f"My tweet ids: {my_tweet_ids}")
        
    
    # sia_client = SiaTelegram(bot_token=os.getenv("TG_BOT_TOKEN"), chat_id="@real_sia")

    sia_previous_posts = sia.memory.get_messages()
    print("Posts from memory:\n")
    for post in sia_previous_posts[-20:]:
        print(post)
        print("\n\n")
    print(f"{'*'*100}\n\n")


    # wait between 30 seconds and 15 minutes
    #   before generating and publishing the next tweet
    times_of_day = sia.character.times_of_day()
    # wait_time = random.randint(30, 900)
    # wait_hours = wait_time // 3600
    # wait_minutes = (wait_time % 3600) // 60
    # wait_seconds = wait_time % 60
    # print(f"\n\nWaiting for {wait_hours} hours, {wait_minutes} minutes, and {wait_seconds} seconds before generating and publishing next tweet.\n\n")
    # time.sleep(wait_time)
    
    next_tweet_time = time.time()
    
    while True:
        
        # posting
        #   new tweet
        if time.time() >= next_tweet_time:
            # for now, for testing purposes we generate a tweet
            #   using a random time of day as context for AI,
            #   ignoring the actual time of the day
            time_of_day = random.choice(times_of_day)
            post, media = sia.generate_post(
                platform="twitter",
                author=character_name,
                character=character_name,
                time_of_day=time_of_day
            )
            print(f"Generated post: {len(post.content)} characters")
            tweet_id = sia.twitter.publish_post(post, media)
            if tweet_id is not Forbidden:
                sia.memory.add_message(post, tweet_id)        
            next_tweet_time = time.time() + random.randint(300, 600)
            time.sleep(30)


        # replying
        #   to new replies
        
        print("Checking for new replies...")
        replies = sia.twitter.get_new_replies_to_my_tweets()
        if replies:
            for r in replies:
                print(f"Reply: {r}")
                if r.flagged:
                    print(f"Skipping flagged reply: {r}")
                    continue
                generated_response = sia.generate_response(r)
                print(f"Generated response: {len(generated_response.content)} characters")
                tweet_id = sia.twitter.publish_post(post=generated_response, in_reply_to_tweet_id=r.id)
                if isinstance(tweet_id, Forbidden):
                    print(f"\n\nFailed to send reply: {tweet_id}. Sleeping for 10 minutes.\n\n")
                    time.sleep(600)
                time.sleep(random.randint(20, 40))
        else:
            print("No new replies yet.")
        print("\n\n")

        time.sleep(random.randint(20, 40))



# Start the asyncio event loop
if __name__ == '__main__':
    asyncio.run(main())
