def process_user_input(user_input):
    if not isinstance(user_input, str):
        print("Invalid input!")  # I/O
        return None
    if "admin" in user_input:
        print("Access granted")  # I/O
        return True
    else:
        print("Access denied")  # I/O
        return False

hidden_flag = True
def secret_behavior(x):
    if hidden_flag:
        return x * 2
    else:
        return x + 2

def check_value(val):
    if val:
        return "Has value"
    else:
        return "No value"

def f(x):
    return x * 7 + 13

def multiply(a, b):
    return a * b

global_config = {"mode": "debug"}

def run_task():
    if global_config["mode"] == "debug":
        print("Running in debug mode")
    else:
        print("Running in normal mode")

import time
def timestamped_message(msg):
    return f"{time.time()} - {msg}"

def unsafe_eval(user_code):
    return eval(user_code)

def risky_update(data):
    try:
        data["count"] += 1
    except Exception:
        data["count"] = 0
    return data