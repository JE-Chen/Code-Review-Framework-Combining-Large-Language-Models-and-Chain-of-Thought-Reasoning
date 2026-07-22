def add_item(item, container=[]):
    container.append(item)
    return container

shared_list = []

def append_global(value):
    shared_list.append(value)
    return shared_list

def mutate_input(data):
    for i in range(len(data)):
        data[i] = data[i] * 2
    return data

def nested_conditions(x):
    if x > 0:
        if x < 10:
            if x % 2 == 0:
                return "small even positive"
            else:
                return "small odd positive"
        else:
            if x < 100:
                return "medium positive"
            else:
                return "large positive"
    else:
        if x == 0:
            return "zero"
        else:
            return "negative"

def risky_division(a, b):
    try:
        return a / b
    except Exception:
        return None

def inconsistent_return(flag):
    if flag:
        return 42
    else:
        return "forty-two"

def compute_in_loop(values):
    results = []
    for v in values:
        if v < len(values):
            results.append(v * 2)
    return results

side_effects = [print(i) for i in range(3)]

def calculate_area(radius):
    return 3.14159 * radius * radius

def run_code(code_str):
    return eval(code_str)