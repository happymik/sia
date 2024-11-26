import json
import time
import random

from utils.logging_utils import setup_logging, log_message, enable_logging

class Character:
    def __init__(self, name=None, intro=None, lore=None, bio=None, traits=None, mood=None, post_examples={}, post_parameters={}, message_examples={}, topics=None, json_file=None, logging_enabled=True):
        if json_file:
            self.load_from_json(json_file)
        else:
            self.name = name
            self.intro = intro
            self.lore = lore
            self.bio = bio
            self.traits = traits
            self.mood = mood
            self.post_examples = post_examples
            self.post_parameters = post_parameters
            self.message_examples = message_examples
            self.topics = topics

        self.logger = setup_logging()
        self.logging_enabled = logging_enabled
        enable_logging(self.logging_enabled)


    def load_from_json(self, json_file):
        with open(json_file, 'r') as file:
            data = json.load(file)
        self.name = data['name'] # required
        self.intro = data['intro'] # required
        self.lore = data['lore'] # required
        self.bio = data.get('bio') # optional
        self.traits = data.get('traits') # optional
        self.mood = data.get('mood') # optional
        self.post_examples = data.get('post_examples') # optional
        self.post_parameters = data.get('post_parameters', {"length_ranges": ["1-5", "20-30", "50-100"]}) # optional
        self.message_examples = data.get('message_examples') # optional
        self.topics = data.get('topics') # optional

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

    def get_mood(self, platform, time_of_day=None):
        """
        Get the character's mood based on the platform and time of day.

        :param platform: The platform (e.g., 'twitter').
        :param time_of_day: The time of day (e.g., 'morning').
        :return: The mood description.
        """
        if time_of_day is None:
            time_of_day = self.current_time_of_day()
        return self.mood.get(platform, {}).get(time_of_day, "morning")

    def get_post_examples(self, platform, time_of_day=None, random_pick=0):
        """
        Get a message example based on the platform and time of day.

        :param platform: The platform (e.g., 'general', 'twitter').
        :param time_of_day: The time of day (e.g., 'morning', 'afternoon', 'evening', 'night').
        :return: A list of message examples.
        """
        if time_of_day is None:
            time_of_day = self.current_time_of_day()
        
        all_examples = self.post_examples.get(platform, {}).get(time_of_day, [])
        if random_pick:
            random.shuffle(all_examples)
            examples_to_return = all_examples[:random_pick]
        else:
            examples_to_return = all_examples
        
        log_message(self.logger, "info", self, f"Post examples: {examples_to_return}")
        
        return examples_to_return

