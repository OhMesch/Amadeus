from enum import Enum, auto

class TransactionType(Enum):
    ELEMENT_ADD = auto()
    ELEMENT_REMOVE = auto()
    LIST_ADD = auto()
    LIST_REMOVE = auto()

class Transaction:
    def __init__(self):
        self.type = None
        self.changes = []

class TransactionTracker:
    def __init__(self):
        self.transactions = []

    def notify(self):
        pass