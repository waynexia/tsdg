import multiprocessing

class Counter:
    def __init__(self, init=0):
        self._value = multiprocessing.Value('i', init)
        self._lock = multiprocessing.Lock()

    def incr(self, n):
        with self._lock:
            self._value.value += n
            return self._value.value

    def decr(self, n):
        with self._lock:
            self._value.value -= n
            return self._value.value

    def value(self):
        with self._lock:
            return self._value.value
