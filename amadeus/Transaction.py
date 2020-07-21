from enum import Enum, auto
import logging


class TransactionType(Enum):

    KEY_CREATE = auto()
    KEY_MODIFY = auto()
    KEY_DELETE = auto()
    LIST_ADD = auto()
    LIST_REMOVE = auto()

# Warning: this entire concept depends on singlethreading
# This also scales infinitley, might want to trim with some ridiculous number (10000)
class Transaction:

    def __init__(self, storage_object, transaction_type, key, old_value = None, new_value = None):
        self.storage_object = storage_object
        self.type = transaction_type
        self.key = key
        self.old_value = old_value
        self.new_value = new_value
    

    def __str__(self):
        return 'transaction_type: {0}, key: {1}, old_value: {2}, new_value: {3}'.format(self.type, self.key, self.old_value, self.new_value)


    def __repr__(self):
        return self.__str__()

class TransactionTracker:

    def __init__(self):
        self.batches = []
        self.pointer_to_batch = 0
        self.temp_transactions = None
        self.pause = False
        self.logger = logging.getLogger('my_fantastical_logger')
        self.logger.warning('__init__: {0} has been created'.format(self.__class__.__name__))


    def notify(self, transaction):
        if not self.pause and self.temp_transactions is not None:
            self.temp_transactions.append(transaction)


    def begin_tracking(self):
        self.logger.warning('Started tracking transactions')
        self.temp_transactions = []


    def end_tracking(self):
        if self.temp_transactions:
            self.batches.append(self.temp_transactions)
            self.pointer_to_batch += 1
        self.temp_transactions = None
        self.logger.warning('Ended tracking transactions')


    def get_batch(self, num):
        want_to_go = num + self.pointer_to_batch
        self.logger.warning('num: {0}, want_to_go: {1}, self.pointer_to_batch: {2}, len(self.batches): {3}'.format(
            num, want_to_go, self.pointer_to_batch, len(self.batches)))
        if want_to_go >= 0 and want_to_go < len(self.batches):
            return self.batches[want_to_go]


    def get_batch_and_adjust(self, num):
        assert(num == 1 or num == -1)
        batch = self.get_batch(num)
        if batch:
            self.pointer_to_batch += num
            return batch


    def undo(self):
        batch = self.get_batch_and_adjust(-1)
        if batch:
            for transaction in batch:
                self.undo_transaction(transaction)
            return batch


    def redo(self):
        batch = self.get_batch_and_adjust(1)
        if batch:
            for transaction in batch:
                self.redo_transaction(transaction)
            return batch


    def undo_transaction(self, transaction: Transaction):
        self.pause = True
        try:
            # first 2 might be the same
            if transaction.type == TransactionType.KEY_CREATE:
                del transaction.storage_object[transaction.key]
            elif transaction.type == TransactionType.KEY_MODIFY:
                transaction.storage_object[transaction.key] = transaction.storage_object.old_value
            elif transaction.type == TransactionType.KEY_DELETE:
                transaction.storage_object[transaction.key] = transaction.storage_object.old_value
            elif transaction.type == TransactionType.LIST_ADD:
                transaction.storage_object.removeFromList(transaction.key, transaction.new_value)
            elif transaction.type == TransactionType.LIST_REMOVE:
                transaction.storage_object.addToList(transaction.key, transaction.old_value)
        except Exception as e:
            self.pause = False
            raise e

    def redo_transaction(self, transaction):
        pass
