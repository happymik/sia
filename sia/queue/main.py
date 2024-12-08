from sia.queue.memory import SiaQueueMemory
from sia.queue.schemas import SiaQueueItem


class SiaQueue:

    def __init__(self, sia):
        self.sia = sia
        self.memory = SiaQueueMemory(self.sia)

    def add_item(self, item: SiaQueueItem):
        self.memory.add_item(item)
    
    def get_items_to_execute(self):
        return self.memory.get_items()
    
    def execute_item(self, item: SiaQueueItem):
        self.memory.update_item(item)

    def run(self):
        items = self.get_items_to_execute()
        for item in items:
            self.execute_item(item)

