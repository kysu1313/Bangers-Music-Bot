import asyncio
import itertools
import random
from asyncio import PriorityQueue
from helpers.ytld_helper import YTDLSource
import heapq

class SongQueue(asyncio.PriorityQueue):
    def __getitem__(self, item):
        if isinstance(item, slice):
            return list(itertools.islice(self._queue, item.start, item.stop, item.step))
        else:
            return self._queue[item]

    #@property
    #def _put(self, item):
    #    self.put(self._queue, item)

    def __iter__(self):
        return self._queue.__iter__()

    def __len__(self):
        return self.qsize()

    def clear(self):
        self._queue.clear()

    def shuffle(self):
        random.shuffle(self._queue)

    def remove(self, index: int):
        del self._queue[index]