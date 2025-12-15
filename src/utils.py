#Don't touch
import random

def weighted_choice(choices):
    total = sum(weight for _, weight in choices)
    r = random.uniform(0, total)
    upto = 0
    for prize, weight in choices:
        if upto + weight >= r:
            return prize
        upto += weight

    return choices[-1][0]
