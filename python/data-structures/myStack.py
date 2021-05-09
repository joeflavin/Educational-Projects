from myLinkedList import myLinkedList

class myStack(myLinkedList):
    def __init__(self):
        super().__init__()


    def push(self, e):
        """ add element to top of stack.
        """
        self.add_first(e)


    def pop(self):
        """ return top object and remove from stack.
        """
        if self.is_empty():
            print("Cannot pop from an empty stack.")
            return None
        top = self.peek()
        self.remove_first()
        return top


    def size(self):
        """ return size of stack.
        """
        return self.get_size()


    def is_empty(self):
        """ return true if stack is empty; false otherwise.
        """
        return super().is_empty()


    def peek(self):
        """ return top object without removing.
        """
        if self.is_empty():
            return None
        return self.__head__.data


    def view(self):
        """ prints the stack to stdout
        """
        if self.is_empty():
            print("Stack is empty.")
        else:
            self.list_traversal()
