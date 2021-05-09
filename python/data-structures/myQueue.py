class myQueue(myLinkedList):
    def __init__(self):
        super().__init__()


    def enqueue(self, e):
        """ insert object at rear of queue.
        """
        self.add_last(e)


    def dequeue(self):
        """ remove and return object at front of queue.
        """
        if self.is_empty():
            print("Cannot dequeue from an empty queue.")
            return None
        front = self.front()
        self.remove_first()
        return front


    def size(self):
        """ return number of objects in queue.
        """
        return self.get_size()


    def is_empty(self):
        """ return true if queue is empty; false otherwise.
        """
        return super().is_empty()


    def front(self):
        """ return, without removing, the object at front of queue.
        """
        if self.is_empty():
            return None
        return self.__head__.data


    def view(self):
        """ prints the queue to stdout
        """
        if self.is_empty():
            print("Queue is empty.")
        else:
            self.list_traversal()
