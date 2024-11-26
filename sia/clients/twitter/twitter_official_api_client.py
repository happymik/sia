import os
import json

import tweepy

from sia.clients.client import SiaClient


class SiaTwitterOfficial(SiaClient):
    
    def __init__(self, api_key, api_secret_key, access_token, access_token_secret):
        super().__init__(
            client=tweepy.Client(
                consumer_key=api_key, consumer_secret=api_secret_key,
                access_token=access_token, access_token_secret=access_token_secret
            )
        ) 

    def publish_post(self, post):
        try:
            response = self.client.create_tweet(text=post)
            print(f"Tweet sent successfully!: {response}")
            return True
        except Exception as e:
            print(f"Failed to send tweet: {e}")
