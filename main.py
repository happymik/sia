import time
import asyncio
import os
import random
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

from sia.sia import Sia
from sia.character import SiaCharacter
from sia.memory.memory import SiaMemory
# from sia.clients.telegram.telegram_client import SiaTelegram
from sia.clients.twitter.twitter_official_api_client import SiaTwitterOfficial

from tweepy import Forbidden


async def main():
    character_name_id = os.getenv("CHARACTER_NAME_ID")

    character = SiaCharacter(json_file=f"characters/{character_name_id}.json")
    sia = Sia(
        character=character,
        twitter=SiaTwitterOfficial(
            api_key=os.getenv("TW_API_KEY"),
            api_secret_key=os.getenv("TW_API_KEY_SECRET"),
            access_token=os.getenv("TW_ACCESS_TOKEN"),
            access_token_secret=os.getenv("TW_ACCESS_TOKEN_SECRET"),
            bearer_token=os.getenv("TW_BEARER_TOKEN")
        ),
        memory=SiaMemory(
            db_path=os.getenv("DB_PATH"),
            character=character
        ),
        logging_enabled=True
    )
    
    character_name = sia.character.name
    
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
    
    tweeted = False

    start_time = time.time()
    
    # run for 45 minutes
    while time.time() - start_time < 2700:

        character_settings = sia.memory.get_character_settings()
        
        next_post_time = character_settings.character_settings.get('twitter', {}).get('next_post_time', 0)
        next_post_datetime = datetime.fromtimestamp(next_post_time).strftime('%Y-%m-%d %H:%M:%S') if next_post_time else "N/A"
        now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"Current time: {now_time}")
        next_post_time_seconds = next_post_time - time.time()
        next_post_hours = next_post_time_seconds // 3600
        next_post_minutes = (next_post_time_seconds % 3600) // 60
        print(f"Next post time: {next_post_datetime} (posting in {next_post_hours}h {next_post_minutes}m)")
        
        # posting
        #   new tweet
        if time.time() > next_post_time:
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
            if tweet_id and tweet_id is not Forbidden:
                sia.memory.add_message(post, tweet_id)
                tweeted = True

                character_settings.character_settings = {
                    "twitter": {
                        "next_post_time": time.time() + sia.character.platform_settings.get("twitter", {}).get("post_frequency", 2) * 3600
                    }
                }
                sia.memory.update_character_settings(character_settings)

            # next_tweet_time = time.time() + random.randint(300, 600)
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
