import random
import time


class Pseudo:
    def sleep(self, min_seconds: int):
        weight = 2.5
        bias = random.random() * min_seconds * weight
        time.sleep(min_seconds + bias)


pseudo = Pseudo()