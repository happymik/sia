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
        self.api_key = api_key
        self.api_secret_key = api_secret_key
        self.access_token = access_token
        self.access_token_secret = access_token_secret


    def publish_post(self, post, media:dict=[]):
        
        if media:
            media_ids = []
            for m in media:
                media_ids.append(
                    self.upload_media(m)
                )
                
        try:
            response = self.client.create_tweet(
                text=post,
                media_ids=media_ids
            )
            print(f"Tweet sent successfully!: {response}")
            return True
        except Exception as e:
            print(f"Failed to send tweet: {e}")


    def upload_media(self, media_filepath):
        auth = tweepy.OAuth1UserHandler(self.api_key, self.api_secret_key)
        auth.set_access_token(
            self.access_token,
            self.access_token_secret,
        )
        client_v1 = tweepy.API(auth)

        media = client_v1.media_upload(filename=media_filepath)
        
        return media.media_id
