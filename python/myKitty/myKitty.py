"""
    My python implementation of a "kitty" app.
"""

class Person:
    def __init__(self, name):
        self.name = name
        self._membership = []     # Is a person a member of an event?
        self.payments = 0
        self.balance = 0


class Transaction:
    def __init__(self, t_name, event, amount, payee):
        self.t_name = t_name
        self.event = event
        self.amount = amount
        self.payee = payee
        self.payee.payments += amount


class Event:
    """ Create an event.

    e_name is a string.
    participants is a list of Person instances.
    """
    def __init__(self, e_name, participants):
        self.e_name = e_name
        self.participants = []
        self._transactions = []
        self.debtors = []
        self.creditors = []
        for person in participants:
            self.add_participant(person)


    def add_participant(self, participant):
        """ Add an individual participant to the event. """
        if isinstance(participant, Person):
            if participant in self.participants:
                print(participant.name, "is already a participant in this event.")
            elif len(participant._membership) == 0:
                participant._membership.append(self.e_name)
                self.participants.append(participant)
            else:
                print(participant.name, "is already a member of an activity. Can join only a single activity at any given time.")
        else:
            print('Error:', participant, 'is not a Person!')


    def add_transaction(self, name, amount, payee):
        """ Register a transaction to the event."""
        if not (isinstance(amount, int) or isinstance(amount, float)):
            print("Error: Amount must be a number.")
        elif amount <= 0:
            print("Error: Amount must be greater than zero.")
        elif payee not in self.participants:
            print("Error:", payee.name, "is not registered to this event.")
        else:
            tr = Transaction(name, self.e_name, amount, payee)
            self._transactions.append(tr)


    def total(self):
        """ Get event total so far """
        total = 0
        for t in self._transactions:
            total += t.amount
        return total


    def costpp(self):
        """" Get Per Person Cost so far """
        return self.total() / len(self.participants)


    def event_clear(self):
        """ Clear person attributes related to event """
        for p in self.participants:
            p.balance = 0
            p.payments = 0
            p._membership = []


    def reconcile(self):
        """ Calculate reconciliations for event """
        totalcost = self.total()
        pp_cost = totalcost / len(self.participants)
        print("Total: €{0:.2f} that is €{1:.2f} each.\n".format(totalcost, pp_cost))
        self.debtors = []       # Clear these now to ensure they are empty
        self.creditors = []
        # For each participant calculate their balance & print results
        for p in self.participants:
            outstanding = p.payments - pp_cost
            print("{0:s} has balance €{1:.2f}.".format(p.name, outstanding))
            p.balance = outstanding
            if outstanding < 0:
                self.debtors.append(p)
            else:
                self.creditors.append(p)
        print()
        """ For each participant in debt compare their debt to each person in
            credit's credit and make payments when possible.
            Then print the payment(s).
        """
        for d in self.debtors:
            for c in self.creditors:
                if abs(d.balance) >= c.balance:
                    amt = c.balance
                    d.balance += amt
                    c.balance = 0
                else:
                    amt = -d.balance
                    c.balance -= amt
                    d.balance = 0
                if amt > 0:
                    print("{0:s} pays {1:s} €{2:.2f}".format(d.name, c.name, amt))
        # Clear participants involvement in the now completed event
        self.event_clear()
