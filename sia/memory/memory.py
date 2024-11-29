from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, asc, desc
from .models_db import SiaMessageModel, Base
from .schemas import SiaMessageSchema, SiaMessageGeneratedSchema
from sia.character import SiaCharacter
import json

from utils.logging_utils import setup_logging, log_message, enable_logging

class SiaMemory:

    def __init__(self, character: SiaCharacter):
        self.db_path = "sqlite:///memory/siamemory.sqlite"
        self.character = character
        self.engine = create_engine(self.db_path)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.logging_enabled = self.character.logging_enabled

        self.logger = setup_logging()
        enable_logging(self.logging_enabled)


    def add_message(self, message: SiaMessageGeneratedSchema, tweet_id: str = None, original_data: dict = None) -> SiaMessageSchema:
        session = self.Session()

        message_model = SiaMessageModel(
            id=tweet_id,
            character=message.character,
            platform=message.platform,
            author=message.author,
            content=message.content,
            conversation_id=message.conversation_id,
            response_to=message.response_to,
            flagged=message.flagged,
            message_metadata=message.message_metadata,
            original_data=original_data
        )

        try:
            # Serialize original_data if it's a dictionary
            if isinstance(original_data, dict):
                original_data = json.dumps(original_data)

            session.add(message_model)
            session.commit()

            # Convert the model to a schema
            message_schema = SiaMessageSchema.from_orm(message_model)
            return message_schema
        
        except Exception as e:
            log_message(self.logger, "error", self, f"Error adding message to database: {e}")
            log_message(self.logger, "error", self, f"message type: {type(message)}")
            session.rollback()
            raise e
        
        finally:
            session.close()
        

    def get_messages(self, id=None, platform: str = None, author: str = None, not_author: str = None, character: str = None, conversation_id: str = None, flagged: bool = False, sort_by: bool = False, sort_order: str = "asc"):
        session = self.Session()
        query = session.query(SiaMessageModel)
        if id:
            query = query.filter_by(id=id)
        if character:
            query = query.filter_by(character=character)
        if platform:
            query = query.filter_by(platform=platform)
        if author:
            query = query.filter_by(author=author)
        if not_author:
            query = query.filter(SiaMessageModel.author != not_author)
        if conversation_id:
            query = query.filter_by(conversation_id=conversation_id)
        query = query.filter_by(flagged=flagged)
        if sort_by:
            if sort_order == "asc":
                query = query.order_by(asc(sort_by))
            else:
                query = query.order_by(desc(sort_by))
        posts = query.all()
        session.close()
        return [SiaMessageSchema.from_orm(post) for post in posts]
    
    def clear_messages(self):
        session = self.Session()
        session.query(SiaMessageModel).filter_by(character=self.character.name).delete()
        session.commit()
        session.close()

    def reset_database(self):
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)
