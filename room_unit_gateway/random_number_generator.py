import numpy as np

def simple_random(min_value: int, max_value: int):
    random_change = np.random.random()
    result = min_value + (max_value - min_value) * random_change
    return min(max(result,min_value),max_value)

def complex_random(min_value: int, max_value: int, precision: int):
    random_change = np.random.random()
    mean = (min_value + max_value) / 2.0
    result = mean * (1 + (precision * (3 * random_change - 1)))
    return min(max(result,min_value),max_value)

def bounce_random(last_value: int, min_value: int, max_value: int, precision: int, alpha: float = 1, decrease: bool = False):
    random_change = np.random.random()
    change_rate = alpha * precision * random_change
    if decrease:
        change_rate = (- 1) * change_rate
    result = last_value + change_rate

    next_decrease = decrease
    if result < min_value:
        next_decrease = False
    elif result > min_value:
        next_decrease = True
    return min(max(result,min_value),max_value), next_decrease

def random_value(last_value: int, min_value: int, max_value: int, precision: int, alpha: float = 0.5):
    mean = (min_value + max_value) / 2.0
    deviation = precision * 2.0
    random_change = np.random.normal(loc = mean, scale = deviation)
    result = last_value + alpha * (random_change - last_value)
    return min(max(result,min_value),max_value)