
from datetime import datetime, timedelta

from sia.queue.schemas import SiaQueueItem

class SiaReasoning:

    def __init__(self, sia):
        self.sia = sia
    
    def add_client_posting(self):
        for client in self.sia.clients:
            if client.memory.posting_enabled:
                if client.memory.get_last_post_time() + timedelta(minutes=client.posting_frequency) < datetime.now():
                    self.sia.queue.add_item(SiaQueueItem(
                        client=client,
                        to_execute_at=datetime.now()
                    ))

    def run(self):
        self.add_client_posting()
