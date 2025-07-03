import numpy as np

def constant(last_value: float = 0.5, min_value: float = 0, max_value: float = 1):
    return min(max(last_value,min_value),max_value)

def binary_random():
    random_change = np.random.random()
    result = 1 if random_change > 0.5 else 0
    return result

def simple_random(min_value: float = 0, max_value: float = 1):
    random_change = np.random.random()
    result = min_value + (max_value - min_value) * random_change
    return min(max(result,min_value),max_value)

def complex_random(min_value: float = 0, max_value: float = 1, precision: float = 0.2):
    random_change = np.random.random()
    mean = (min_value + max_value) / 2.0
    result = mean * (1 + (precision * (3 * random_change - 1)))
    return min(max(result,min_value),max_value)

def bounce_random(last_value: float = 0.5, min_value: float = 0, max_value: float = 1, precision: float = 0.2, alpha: float = 0.5, decrease: bool = False):
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

def random_value(last_value: float = 0.5, min_value: float = 0, max_value: float = 1, precision: float = 0.2, alpha: float = 0.5):
    mean = (min_value + max_value) / 2.0
    deviation = precision * 2.0
    random_change = np.random.normal(loc = mean, scale = deviation)
    result = last_value + alpha * (random_change - last_value)
    return min(max(result,min_value),max_value)

def predefined_sequence(min_value: float = 0, max_value: float = 1, seed: int = 0, index: int = 0):
    sequence = [[0,0.1,0.2,0.3,0.4,0.5,0.4,0.5,0.6,0.7,0.8,0.7,0.6,0.7,0.8,0.9,1],[0,0.1,0.2,0.3,0.4,0.5,0.4,0.5,0.6,0.7,0.8,0.7,0.6,0.7,0.8,0.9,1]]
    chosen_sequence = sequence[seed % len(sequence)]
    random_change = chosen_sequence[index % len(chosen_sequence)]
    result = min_value + (max_value - min_value) * random_change
    return min(max(result,min_value),max_value)
