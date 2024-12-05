import os
import json
import time
import random
from datetime import datetime

import tweepy
from tweepy import Tweet, Forbidden

from sia.clients.client import SiaClient
from sia.memory.schemas import SiaMessageGeneratedSchema, SiaMessageSchema
from sia.memory.memory import SiaMemory
from sia.character import SiaCharacter
from utils.logging_utils import setup_logging, log_message, enable_logging

class SiaTwitterOfficial(SiaClient):
    
    def __init__(self, api_key, api_secret_key, access_token, access_token_secret, bearer_token, sia = None, character: SiaCharacter = None, memory: SiaMemory = None, logging_enabled=True):
        super().__init__(
            client=tweepy.Client(
                consumer_key=api_key, consumer_secret=api_secret_key,
                access_token=access_token, access_token_secret=access_token_secret,
                bearer_token=bearer_token
            )
        )

        self.logger = setup_logging()
        enable_logging(logging_enabled)

        self.api_key = api_key
        self.api_secret_key = api_secret_key
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.memory = memory
        self.character = character
        self.sia = sia


    def publish_post(self, post:SiaMessageGeneratedSchema, media:dict=[], in_reply_to_tweet_id:str=None) -> str:
        
        media_ids = None
        if media:
            media_ids = []
            for m in media:
                media_ids.append(
                    self.upload_media(m)
                )
        
        try:
            print(f"post: {post}")
            print(f"media_ids: {media_ids}")
            print(f"in_reply_to_tweet_id: {in_reply_to_tweet_id}")
            
            response = self.client.create_tweet(
                text=post.content,
                **({"media_ids": media_ids} if media_ids else {}),
                # in_reply_to_tweet_id=in_reply_to_tweet_id
                **({"in_reply_to_tweet_id": in_reply_to_tweet_id} if in_reply_to_tweet_id else {})
            )
            print(f"Tweet sent successfully!: {response}")
            return response.data['id']
        except Exception as e:
            print(f"Failed to send tweet: {e}")
            print(f"Response headers: {e.response.headers}")


    def upload_media(self, media_filepath):
        auth = tweepy.OAuth1UserHandler(self.api_key, self.api_secret_key)
        auth.set_access_token(
            self.access_token,
            self.access_token_secret,
        )
        client_v1 = tweepy.API(auth)

        media = client_v1.media_upload(filename=media_filepath)
        
        return media.media_id


    def get_my_tweet_ids(self):
        log_message(self.logger, "info", self, f"Getting my tweet ids for {self.character.twitter_username}")
        my_tweets = self.memory.get_messages(platform="twitter", author=self.character.twitter_username)
        return [tweet.id for tweet in my_tweets]
    
    
    def get_last_retrieved_reply_id(self):
        replies = self.memory.get_messages(platform="twitter", not_author=self.character.name)
        if replies:
            return max(replies, key=lambda reply: reply.id).id


    def get_new_replies_to_my_tweets(self) -> list[SiaMessageSchema]:
        since_id = self.get_last_retrieved_reply_id()

        # sorted to process newer tweets first
        my_tweet_ids = sorted(self.get_my_tweet_ids(), key=int, reverse=True)

        log_message(self.logger, "info", self, f"since_id: {since_id}")
        log_message(self.logger, "info", self, f"my_tweet_ids: {my_tweet_ids}")

        messages = []

        for i in range(0, len(my_tweet_ids), 10):
            time.sleep(61)
            batch = my_tweet_ids[i:i+10]
            query = " OR ".join([f"conversation_id:{id}" for id in batch])
            log_message(self.logger, "info", self, f"query: {query}")

            try:
                new_replies_to_my_tweets = self.client.search_recent_tweets(
                    query=query,
                    since_id=since_id,
                    tweet_fields=["conversation_id","created_at","in_reply_to_user_id"],
                    expansions=["author_id","referenced_tweets.id"]
                )
            except Exception as e:
                log_message(self.logger, "error", self, f"Error getting replies: {e}")
                continue
            
            if not new_replies_to_my_tweets.data:
                continue
            
            for reply in new_replies_to_my_tweets.data:
                
                # exclude replies from the character itself
                author = next((user.username for user in new_replies_to_my_tweets.includes['users'] if user.id == reply.author_id), None)
                log_message(self.logger, "info", self, f"author of the received reply: {author}")
                if author == self.character.twitter_username:
                    continue
                
                try:
                    from openai import OpenAI
                    client = OpenAI()
                    moderation_response = client.moderations.create(
                        model="omni-moderation-latest",
                        input=reply.text,
                    )
                    flagged = moderation_response.results[0].flagged
                    if flagged:
                        log_message(self.logger, "info", self, f"flagged reply: {reply.text}")
                except Exception as e:
                    log_message(self.logger, "error", self, f"Error moderating reply: {e}")
                    flagged = False

                try:
                    message = self.memory.add_message(
                        SiaMessageGeneratedSchema(
                            conversation_id=str(reply.data['conversation_id']),
                            content=reply.text,
                            platform="twitter",
                            author=next(user.username for user in new_replies_to_my_tweets.includes['users'] if user.id == reply.author_id),
                            response_to=str(next((ref.id for ref in reply.referenced_tweets if ref.type == "replied_to"), None)) if reply.referenced_tweets else None,
                            wen_posted=reply.created_at,
                            flagged=int(flagged),
                            metadata=moderation_response
                        ),
                        tweet_id=str(reply.id),
                        original_data=reply.data
                    )
                    messages.append(message)
                except Exception as e:
                    log_message(self.logger, "error", self, f"Error adding message: {e}")

        return messages


    def get_conversation(self, conversation_id: str) -> list[SiaMessageSchema]:
        messages = self.memory.get_messages(conversation_id=conversation_id, sort_by="wen_posted", sort_order="asc", flagged=False)
        return messages



    async def run(self):

        if not self.character.platform_settings.get("twitter", {}).get("enabled", True):
            return
        
        while 1:

            character_settings = self.memory.get_character_settings()
            
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
                post, media = self.sia.generate_post(
                    platform="twitter",
                    author=self.character.twitter_username,
                    character=self.character.name
                )
                
                if post or media:
                    print(f"Generated post: {len(post.content)} characters")
                    tweet_id = self.publish_post(post, media)
                    if tweet_id and tweet_id is not Forbidden:
                        self.memory.add_message(message_id=tweet_id, message=post)

                        character_settings.character_settings = {
                            "twitter": {
                                "next_post_time": time.time() + self.character.platform_settings.get("twitter", {}).get("post_frequency", 2) * 3600
                            }
                        }
                        self.memory.update_character_settings(character_settings)
                else:
                    log_message(self.logger, "info", self, "No post or media generated.")

                time.sleep(30)


            # replying
            #   to new replies
            
            if self.character.responding.get("enabled", True):
                print("Checking for new replies...")
                replies = self.get_new_replies_to_my_tweets()
                if replies:
                    
                    # randomize the order of replies
                    replies.sort(key=lambda x: random.random())
                    
                    for r in replies:
                        
                        max_responses_an_hour = character_settings.character_settings.get("responding", {}).get("responses_an_hour", 3)
                        log_message(self.logger, "info", self, f"Replies sent during this hour: {replies_sent}, max allowed: {max_responses_an_hour}")
                        if replies_sent >= max_responses_an_hour:
                            break

                        print(f"Reply: {r}")
                        if r.flagged:
                            print(f"Skipping flagged reply: {r}")
                            continue
                        generated_response = self.generate_response(r)
                        if not generated_response:
                            print(f"No response generated for reply: {r}")
                            continue
                        print(f"Generated response: {len(generated_response.content)} characters")
                        tweet_id = self.sia.twitter.publish_post(post=generated_response, in_reply_to_tweet_id=r.id)
                        replies_sent += 1
                        if isinstance(tweet_id, Forbidden):
                            print(f"\n\nFailed to send reply: {tweet_id}. Sleeping for 10 minutes.\n\n")
                            time.sleep(600)
                        time.sleep(random.randint(20, 40))
                else:
                    print("No new replies yet.")
                print("\n\n")

            time.sleep(random.randint(20, 40))


