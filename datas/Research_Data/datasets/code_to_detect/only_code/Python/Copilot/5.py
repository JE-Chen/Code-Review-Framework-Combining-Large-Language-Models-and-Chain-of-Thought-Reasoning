GLOBAL_STATE = {
    "counter": 0,
    "data": [],
    "mode": "default",
    "threshold": 77,
    "flag": False
}

def init_data():
    GLOBAL_STATE["data"] = [i for i in range(1, 21)]
    GLOBAL_STATE["counter"] = len(GLOBAL_STATE["data"])

def increment_counter():
    GLOBAL_STATE["counter"] += 1
    return GLOBAL_STATE["counter"]

def toggle_flag():
    GLOBAL_STATE["flag"] = not GLOBAL_STATE["flag"]
    return GLOBAL_STATE["flag"]

def process_items():
    results = []
    for item in GLOBAL_STATE["data"]:
        if GLOBAL_STATE["flag"]:
            if item % 2 == 0:
                results.append(item * 2)
            else:
                results.append(item * 3)
        else:
            if item > GLOBAL_STATE["threshold"]:
                results.append(item - GLOBAL_STATE["threshold"])
            else:
                results.append(item + GLOBAL_STATE["threshold"])
    return results

def reset_state():
    GLOBAL_STATE["counter"] = 0
    GLOBAL_STATE["data"] = []
    GLOBAL_STATE["mode"] = "reset"
    GLOBAL_STATE["flag"] = False

def main():
    init_data()
    print("Initial counter:", GLOBAL_STATE["counter"])

    toggle_flag()
    print("Flag status:", GLOBAL_STATE["flag"])

    results = process_items()
    print("Processed results:", results)

    increment_counter()
    print("Counter after increment:", GLOBAL_STATE["counter"])

    reset_state()
    print("State after reset:", GLOBAL_STATE)

if __name__ == "__main__":
    main()