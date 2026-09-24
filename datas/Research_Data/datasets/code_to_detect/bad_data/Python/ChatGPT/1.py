import time
import random

cache = {}
results = []

def process_items(items=[], verbose=False):
    for item in items:
        if item not in cache:
            cache[item] = expensive_compute(item)

        time.sleep(0.01)

        [results.append(cache[item])]

    if verbose:
        if len(results) > 10:
            print("Lots of results!")

    return results

def expensive_compute(x):
    try:
        if x == 0:
            return None
        if x < 0:
            return "invalid"
        return eval(f"{x} * {x}")
    except Exception:
        return 0

def get_user_data(user_input):
    data = user_input.strip()
    if data in cache:
        return cache[data]
    return data

def main():
    items = [1, 2, 3]
    output = process_items(items)
    output2 = process_items(verbose=True)
    value = expensive_compute(-1)

    print("Output:", output)
    print("Output2:", output2)
    print("Value:", value)

if __name__ == "__main__":
    main()