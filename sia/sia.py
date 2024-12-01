import datetime
import time
import random
import os
from uuid import uuid4

from sia.character import SiaCharacter
from sia.clients.client import SiaClient
from sia.memory.memory import SiaMemory
from sia.memory.schemas import SiaMessageGeneratedSchema, SiaMessageSchema

from plugins.imgflip_meme_generator import ImgflipMemeGenerator

from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from utils.etc_utils import generate_image_dalle, save_image_from_url
from utils.logging_utils import setup_logging, log_message, enable_logging


class Sia:
    
    def __init__(self, character: SiaCharacter, memory: SiaMemory = None, clients = None, twitter = None, logging_enabled=True):
        self.character = character
        if not self.character.sia:
            self.character.sia = self
        self.memory = memory if memory else SiaMemory(character=character)
        self.clients = clients
        self.twitter = twitter
        self.twitter.character = self.character
        self.twitter.memory = self.memory
        print(f"twitter memory: {self.twitter.memory}")
        print(f"twitter character: {self.twitter.character}")

        self.logger = setup_logging()
        enable_logging(logging_enabled)
        self.character.logging_enabled = logging_enabled


    def generate_post(self, platform="twitter", author=None, character=None, time_of_day=None):

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """
                {you_are}
                
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
        
        ai_input = {
            "you_are": self.character.prompts.get("you_are"),
            "post_examples": self.character.get_post_examples("general", time_of_day=time_of_day, random_pick=7),
            "previous_posts": [f"[{post.wen_posted}] {post.content}" for post in self.memory.get_messages()[-10:]],
            "platform": platform,
            "length_range": random.choice(self.character.post_parameters.get("length_ranges")),
            # "formatting": self.character.post_parameters.get("formatting")
        }
        
        try: 
            llm = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0.3)
            
            ai_chain = prompt_template | llm

            generated_post = ai_chain.invoke(ai_input)
            
            log_message(self.logger, "info", self, f"Generated post with Anthropic: {generated_post}")
            
        except Exception as e:
            
            try:
                llm = ChatOpenAI(model="gpt-4o", temperature=0.0)
                
                ai_chain = prompt_template | llm

                generated_post = ai_chain.invoke(ai_input)

                log_message(self.logger, "info", self, f"Generated post with OpenAI: {generated_post}")
            
            except Exception as e:
                
                generated_post = None
                
                log_message(self.logger, "error", self, f"Error generating post: {e}")
        
        
        image_filepaths = []
        
        # Generate an image for the post
        if random.random() < self.character.plugins_settings.get("dalle", {}).get("probability_of_posting", 0):
            image_url = generate_image_dalle(generated_post.content[0:900])
            if image_url:
                image_filepath = f"media/{uuid4()}.png"
                save_image_from_url(image_url, image_filepath)
                image_filepaths.append(image_filepath)


        # Generate a meme for the post
        imgflip_meme_generator = ImgflipMemeGenerator(os.getenv("IMGFLIP_USERNAME"), os.getenv("IMGFLIP_PASSWORD"))
        if random.random() < self.character.plugins_settings.get("imgflip", {}).get("probability_of_posting", 0):
            print("Generating a meme")
            image_url = imgflip_meme_generator.generate_ai_meme(prefix_text=generated_post.content)
            if image_url:
                os.makedirs("media/imgflip_memes", exist_ok=True)
                image_filepath = f"media/imgflip_memes/{uuid4()}.png"
                save_image_from_url(image_url, image_filepath)
                image_filepaths.append(image_filepath)


        post_content = generated_post.content if generated_post else None
        generated_post_schema = SiaMessageGeneratedSchema(
            content=post_content,
            platform=platform,
            author=self.character.twitter_username,
            character=self.character.name
        )

        return generated_post_schema, image_filepaths


    def generate_response(self, message: SiaMessageSchema, platform="twitter", time_of_day=None) -> SiaMessageGeneratedSchema|None:
        """
        Generate a response to a message.
        
        Output:
        - SiaMessageGeneratedSchema
        - None if an error occurred or if filtering rules are not passed
        """


        # do not answer if responding is disabled
        if not self.character.responding.get("enabled", True):
            return None


        conversation = self.twitter.get_conversation(conversation_id=message.conversation_id)
        conversation_first_message = self.memory.get_messages(id=message.conversation_id, platform=platform)
        conversation = conversation_first_message + conversation
        
        message_to_respond_str = f"[{message.wen_posted}] {message.author}: {message.content}"
        log_message(self.logger, "info", self, f"Message to respond: {message_to_respond_str}")
        conversation_str = "\n".join([f"[{msg.wen_posted}] {msg.author}: {msg.content}" for msg in conversation])
        log_message(self.logger, "info", self, f"Conversation: {conversation_str}")
        
                
        # do not answer if the message does not pass the filtering rules
        if self.character.responding.get("filtering_rules"):
            log_message(self.logger, "info", self, f"Checking the response against filtering rules: {self.character.responding.get('filtering_rules')}")
            llm_filtering = ChatOpenAI(model="gpt-4o-mini", temperature=0.0)
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", """
                    You are a message filtering AI. You are given a message and a list of filtering rules. You need to determine if the message passes the filtering rules. If it does, return 'True'. If it does not, return 'False' Only respond with 1 word: 'True' or 'False'.
                """),
                ("user", """
                    Conversation:
                    {conversation}

                    Message from the conversation to decide whether to respond to:
                    {message}
                    
                    Filtering rules:
                    {filtering_rules}
                """)
            ])
            filtering_chain = prompt_template | llm_filtering
            filtering_result = filtering_chain.invoke({"conversation": conversation_str, "message": message_to_respond_str, "filtering_rules": self.character.responding.get("filtering_rules")})
            log_message(self.logger, "info", self, f"Response filtering result: {filtering_result.content}")

            if filtering_result.content.lower() == "false":
                return None
        else:
            log_message(self.logger, "info", self, f"No filtering rules found.")

        
        time_of_day = time_of_day if time_of_day else self.character.current_time_of_day()
        
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """
                {you_are}
                
                {communication_requirements}
                
                Your goal is to respond to the message on {platform} provided below in the conversation provided below.
                
                Message to response:
                {message}

                Conversation:
                {conversation}
            """),
            ("user", """
                Generate your response to the message. Your response length must be fewer than 30 words.
            """)
        ])

        ai_input = {
            "you_are": self.character.prompts.get("you_are"),
            "communication_requirements": self.character.prompts.get("communication_requirements"),
            "platform": platform,
            "message": message_to_respond_str,
            "conversation": conversation_str
        }
        
        try: 
            llm = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0.3)
            
            ai_chain = prompt_template | llm

            generated_response = ai_chain.invoke(ai_input)
            
        except Exception as e:
            
            try:
                llm = ChatOpenAI(model="gpt-4o", temperature=0.0)
                
                ai_chain = prompt_template | llm

                generated_response = ai_chain.invoke(ai_input)
            
            except Exception as e:
                generated_response = None
                log_message(self.logger, "error", self, f"Error generating response: {e}")
                return None
        
        
        if not generated_response:
            return None
        

        generated_response_schema = SiaMessageGeneratedSchema(
            content=generated_response.content,
            platform=platform,
            author=self.character.name,
            character=self.character.name,
            response_to=message.id
        )
        log_message(self.logger, "info", self, f"Generated response: {generated_response_schema}")

        return generated_response_schema


    def publish_post(self, client: SiaClient, post: SiaMessageGeneratedSchema, media: dict = []) -> str:
        tweet_id = client.publish_post(post, media)
        return tweet_id


    # def generate_response(self, message):
    #     pass


    # def create_queue(self):
        
    #     queue = []
        
    #     # check if it is time to post
        
    #     # check if there are conversations to respond to
        
    #     pass
