import unittest
import contextlib
from io import StringIO


class testLinkedList(unittest.TestCase):

    def test_LList_newSize(self):
        """ New list has size 0.
        """
        ll = myLinkedList()
        self.assertEqual(0, ll.get_size())


    def test_LList_newEmpty(self):
        """ is_empty() method returns True for a new list.
        """
        ll = myLinkedList()
        self.assertTrue(ll.is_empty())


    def test_LList_addFrontSize(self):
        """ Size is 1 for a new list with one item added to front.
        """
        ll = myLinkedList()
        ll.add_first(1)
        self.assertEqual(1, ll.get_size())


    def test_LList_addRearSize(self):
        """ Size is 1 for a new list with one item added to rear.
            .
        """
        ll = myLinkedList()
        ll.add_last(2)
        self.assertEqual(1, ll.get_size())


    def test_LList_addBothSize(self):
        """ Size is 2 for a new list with one added to front, one to rear.
        """
        ll = myLinkedList()
        ll.add_first(1)
        ll.add_last(2)
        self.assertEqual(2, ll.get_size())


    def test_LList_addEmptyFalse(self):
        """ is_empty() method returns False for list with one added item.
        """
        ll = myLinkedList()
        ll.add_first(1)
        self.assertFalse(ll.is_empty())


    def test_LList_removeSize(self):
        """ Size is 2 for list with three items added, one removed.
        """
        a = 1
        b = 2
        c = 3
        ll = myLinkedList()
        ll.add_first(a)
        ll.add_last(b)
        ll.add_first(c)
        ll.remove_first()
        self.assertEqual(2, ll.get_size())


    def test_LList_removeEmptySize(self):
        """ is_empty() method returns True for list with three items added, three removed.
        """
        a = 1
        b = 2
        c = 3
        ll = myLinkedList()
        ll.add_first(a)
        ll.add_first(b)
        ll.add_last(c)
        ll.remove_first()
        ll.remove_first()
        ll.remove_first()
        self.assertTrue(ll.is_empty())


    def test_LList_removeFromEmptyList(self):
        """ Warning is printed when removing item from empty list.
        """
        a = 1
        b = 2
        c = 3
        ll = myLinkedList()
        ll.add_first(a)
        ll.add_first(b)
        ll.add_last(c)
        ll.remove_first()
        ll.remove_first()
        ll.remove_first()
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            ll.remove_first()
        output = temp_stdout.getvalue().strip()
        assert output == "Cannot remove item from an empty list."


    def test_LList_traversal(self):
        """ Printed output as expected when traversing a list of three items.
        """
        a = 2
        b = 1
        c = 3
        ll = myLinkedList()
        ll.add_first(a)
        ll.add_first(b)
        ll.add_last(c)
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            ll.list_traversal()
        output = temp_stdout.getvalue().strip()
        assert output == "1\n2\n3\nFinished!"



class testStack(unittest.TestCase):

    def test_Stack_newEmpty(self):
        """ is_empty() method returns True for new stack.
        """
        s = myStack()
        self.assertTrue(s.is_empty())


    def test_Stack_push(self):
        """ Push an item onto new stack. Size is now 1.
        """
        s = myStack()
        s.push(1)
        self.assertEqual(1, s.get_size())


    def test_Stack_pushTwice(self):
        """ Push two items onto new stack. Size is now 2.
        """
        s = myStack()
        s.push(1)
        s.push(1)
        self.assertEqual(2, s.get_size())


    def test_Stack_pop(self):
        """ On new stack push two items, pop one. Size is now 1.
        """
        s = myStack()
        s.push(1)
        s.push(2)
        result = s.pop()
        self.assertEqual(result, 2)
        self.assertEqual(1, s.get_size())


    def test_Stack_popTwice(self):
        """ On new stack push two items, pop two. Last popped item is first item pushed. Size is now 0.
        """
        s = myStack()
        s.push(1)
        s.push(2)
        s.pop()
        result = s.pop()
        self.assertEqual(result, 1)
        self.assertEqual(0, s.get_size())


    def test_Stack_peek(self):
        """ Peek at top item of a stack. It is last item pushed onto stack.
        """
        s = myStack()
        s.push(1)
        s.push(2)
        s.push(3)
        self.assertEqual(3, s.peek())


    def test_StackEmpty_peek(self):
        """ peek() method return value is None for empty stack."""
        s = myStack()
        self.assertIsNone(s.peek())


    def test_Stack_popFromEmptyStack(self):
        """ Attempt to pop another item from now empty stack. Warning message is printed. return value is None.
        """
        s = myStack()
        s.push(1)
        s.push(2)
        s.push(3)
        s.pop()
        s.pop()
        s.pop()
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            result = s.pop()
        output = temp_stdout.getvalue().strip()
        assert output == "Cannot pop from an empty stack."
        self.assertEqual(result, None)


    def test_Stack_viewEmpty(self):
        """ view() method prints warning for empty stack.
        """
        s = myStack()
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            s.view()
        output = temp_stdout.getvalue().strip()
        assert output == "Stack is empty."



class testQueue(unittest.TestCase):

    def test_Queue_newEmpty(self):
        """ is_empty() method returns True for new queue.
        """
        q = myQueue()
        self.assertTrue(q.is_empty())


    def test_Queue_enqueueSize(self):
        """ Enqueue one item onto new Queue. Size is now 1.
        """
        q = myQueue()
        q.enqueue(1)
        self.assertEqual(1, q.size())


    def test_Queue_enqueueDequeue(self):
        """ Enqueue three items, Dequeue one. Item returned is first item enqueued. Size is now 2.
        """
        q = myQueue()
        q.enqueue(1)
        q.enqueue(2)
        q.enqueue(3)
        self.assertEqual(3, q.size())
        result = q.dequeue()
        self.assertEqual(result, 1)
        self.assertEqual(2, q.size())


    def test_Queue_front(self):
        """ Enqueue three items. front() method returns first item enqueued. Size remains unchanged.
        """
        q = myQueue()
        q.enqueue(1)
        q.enqueue(2)
        q.enqueue(3)
        size = q.size()
        self.assertEqual(1, q.front())
        self.assertEqual(size, q.size())


    def test_StackEmpty_peek(self):
        """ front() method value is None for empty queue."""
        s = myQueue()
        self.assertIsNone(s.front())


    def test_Queue_dequeueFromEmptyQueue(self):
        """ Attempt to dequeue from empty queue. Warning message is printed. return value is None.
        """
        q = myQueue()
        q.enqueue(1)
        q.enqueue(2)
        q.enqueue(3)
        q.dequeue()
        q.dequeue()
        q.dequeue()
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            result = q.dequeue()
        output = temp_stdout.getvalue().strip()
        assert output == "Cannot dequeue from an empty queue."
        self.assertEqual(result, None)


    def test_Queue_viewEmpty(self):
        """ view() method prints warning for empty queue.
        """
        q = myQueue()
        temp_stdout = StringIO()
        with contextlib.redirect_stdout(temp_stdout):
            q.view()
        output = temp_stdout.getvalue().strip()
        assert output == "Queue is empty."



unittest.main(argv=[''], verbosity=2, exit=False)
        
