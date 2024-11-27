import datetime
import time
import random
import os
from uuid import uuid4

from sia.character import Character
from sia.clients.client import SiaClient
from sia.memory.memory import SiaMemory

from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from utils.etc_utils import generate_image_dalle, save_image_from_url
from utils.logging_utils import setup_logging, log_message, enable_logging


class Sia:
    
    def __init__(self, character: Character, memory: SiaMemory = None, clients = None, logging_enabled=True):
        self.character = character
        self.memory = memory
        self.clients = clients

        self.logger = setup_logging()
        enable_logging(logging_enabled)
        self.character.logging_enabled = logging_enabled


    def times_of_day(self):
        return ["morning", "afternoon", "evening", "night"]

    def current_time_of_day(self):
        current_hour = time.localtime().tm_hour
        if 5 <= current_hour < 12:
            time_of_day = "morning"
        elif 12 <= current_hour < 17:
            time_of_day = "afternoon"
        elif 17 <= current_hour < 21:
            time_of_day = "evening"
        else:
            time_of_day = "night"
        
        return time_of_day


    def generate_post(self, time_of_day=None, platform="twitter"):

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """
                You are {character_name}: {character_intro}.
                
                Here's more about you:
                {character_lore}.
                
                Current date and time: {current_date_time}.
                
                Your current mood is {mood}.
                
                Your post examples are:
                {post_examples}
                
                Use these examples as an inspiration for the new posts you create.
                
                Here are your previous posts:
                {previous_posts}
                
                You are posting to: {platform}
            """),
            ("user", """
                Generate your new post.

                Critically important: your new post must be different from the examples provided and from your previous posts in all ways, shapes or forms.
                
                Examples:
                - if one of your previous posts starts with "Good morning", your new post must not start with "Good morning"
                - if one of your previous posts starts with an emoji, your new post must not start with an emoji
                - if one of your previous posts has a structure like "Question: <question> Answer: <answer>", your new post must not have that structure
                
                Your post must be between {length_range} words long.
                
                You must not use hashtags in your post.
            """)
        ])
        
        # llm = ChatOpenAI(model="gpt-4o", temperature=0.0)
        llm = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0.3)
        
        ai_chain = prompt_template | llm

        ai_input = {
            "character_name": self.character.name, 
            "character_intro": self.character.intro,
            "character_lore": self.character.lore,
            "current_date_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mood": self.character.get_mood("general", time_of_day=time_of_day),
            "post_examples": self.character.get_post_examples("general", time_of_day=time_of_day, random_pick=7),
            "previous_posts": [f"[{post[5]}] {post[4]}" for i, post in enumerate(self.memory.get_posts()[-10:])],
            "platform": platform,
            "length_range": random.choice(self.character.post_parameters.get("length_ranges")),
            # "formatting": self.character.post_parameters.get("formatting")
        }

        post = ai_chain.invoke(ai_input)
        
        # Generate an image for the post
        #   with 30% probability before we have a way for Sia
        #   to decide herself when to generate
        image_filepath = None
        if random.random() < 0.3:
            image_url = generate_image_dalle(post.content[0:900])
            image_filepath = f"media/{uuid4()}.png"
            save_image_from_url(image_url, image_filepath)

        return post.content, image_filepath


    def publish_post(self, client: SiaClient, post: str, media: dict = []):
        client.publish_post(post, media)


    # def generate_response(self, message):
    #     pass


    # def create_queue(self):
        
    #     queue = []
        
    #     # check if it is time to post
        
    #     # check if there are conversations to respond to
        
    #     pass
