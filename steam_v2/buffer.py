import collections
import pandas as pd
import numpy as np

class Buffer:
    def __init__(self, size=None):
        self.queue = collections.deque([], size)

    def append(self, value):
        self.queue.append(value)
        return self.to_array()

    def appendleft(self, value):
        self.queue.appendleft(value)
        return self.to_array()

    def extend(self, value):
        self.queue.extend(value)
        return self.to_array()
        # e.g., [1, 2, 3].extendleft([6, 7, 8]) = [8, 7, 6, 1, 2, 3]
    def extendleft(self, value):
        self.queue.extendleft(value)
        return self.to_array()
        # to be used when it is a 1xn array
    def to_series(self):
        return pd.Series(list(self.queue))
        # to be used when the deque is a list of jsons
    def to_dataframe(self, columns=None):
        return pd.DataFrame.from_records(map(json.loads, list(self.queue)))

    def to_array(self):
        return np.array(self.queue)

    def clear(self):
        self.queue.clear()

    def scan(self, data):
        yield [self.append(item) for item in data]
