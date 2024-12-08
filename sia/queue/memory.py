from sia.queue.schemas import SiaQueueItem

class SiaQueueMemory:

    def __init__(self, sia):
        self.sia = sia
        self.queue = []

    def add_item(self, item: SiaQueueItem):
        self.queue.append(item)
    
    def get_items(self):
        return self.queue

    def update_item(self, item: SiaQueueItem):
        for i, queue_item in enumerate(self.queue):
            if queue_item.id == item.id:
                self.queue[i] = item
                break
