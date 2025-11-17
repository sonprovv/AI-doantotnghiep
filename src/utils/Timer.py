import time

class Timer:
    def __init__(self):
        self.start_time = time.time()

    def elapsed_ms(self):
        return (time.time() - self.start_time) * 1000

    def reset(self):
        self.start_time = time.time()
