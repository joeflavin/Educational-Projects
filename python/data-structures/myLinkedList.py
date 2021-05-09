class myLinkedList:
    def __init__(self):
        self.__nodes__ = 0
        self.__head__ = None
        self.__tail__ = None
        self.listNode = self.listNode

    class listNode:
        """ (Inner) Class to implement linked list nodes.

            Nodes have a data attribute.
            Nodes point to next node in the list with their next attribute.
        """
        def __init__(self, data = None):
            self.data = data
            self.next = None


    def add_first(self, e):
        """ add an element at the head.
        """
        new_node = self.listNode(e)            # make a new node
        new_node.next = self.__head__          # link the new node to previous first node (or None)
        self.__head__ = new_node               # Point the head to the new node
        if self.__tail__ ==  None:             # In the special-case of an initially empty list
            self.__tail__ = new_node                # also point the tail to the only node - the new node
        self.__nodes__ += 1                    # increment list size counter


    def add_last(self, e):
        """ add an element at the tail.
        """
        new_node = self.listNode(e)            # make a new node
        new_node.next = None                   # It is last node so point it to None
        if self.__tail__ != None:              # If the tail points to something
            self.__tail__.next = new_node           # Let that something now point to the new node
        self.__tail__ = new_node               # Now point the tail to the new node
        if self.__head__ == None:              # If head is None our list was initially empty
            self.__head__ = new_node                # so point the head to the newly inserted node also
        self.__nodes__ += 1                    # increment list size counter


    def remove_first(self):
        """ remove the element at the head.
        """
        if self.is_empty():
            print("Cannot remove item from an empty list.")
            return
        first_node = self.__head__             # find element at the head
        self.__head__ = first_node.next        # set head to second node (or None)
        first_node.next = None                 # Un-link initial first node - removes it from the list
        self.__nodes__ -= 1


    def list_traversal(self):
        """ print all elements in list from head to tail.
        """
        current = self.__head__               # Set current to be the first node
        while current != None:                # current will be None after visiting last node
            print(current.data)                   # print the current node's data
            current = current.next                # now visit the next node
        print("Finished!")


    def get_size(self):
        """ return size of the list.
        """
        return self.__nodes__


    def is_empty(self):
        """ return true if list empty; false otherwise.
        """
        if self.get_size() == 0:
            return True
        return False
