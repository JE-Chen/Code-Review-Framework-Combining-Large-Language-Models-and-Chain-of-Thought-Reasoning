## PR Summary Template

### Summary Rules
#### Key Changes
- Added functionality to filter users based on certain criteria during loading.
- Implemented caching mechanism to store processed users.
- Created functions to calculate average scores and find top users.
- Added formatting options for user data.

#### Impact Scope
- `loadAndProcessUsers`: Responsible for loading and processing user data.
- `calculateAverage`: Calculates the average score of users.
- `getTopUser`: Finds the top-performing user.
- `formatUser`: Formats user information into a readable string.
- `mainProcess`: Orchestrates the entire process from data loading to displaying results.

#### Purpose of Changes
- To enhance the system's ability to handle and analyze user data efficiently.
- To improve the modularity and reusability of the code.
- To provide better insights into user performance through metrics and summaries.

#### Risks and Considerations
- Potential performance issues with large datasets due to caching.
- The caching mechanism may need adjustments based on memory constraints.
- Ensure that user data is handled securely and that sensitive information is not exposed.

#### Items to Confirm
- Validate the correctness of the filtering logic.
- Check if the caching mechanism is effective and does not impact performance negatively.
- Ensure that all edge cases and error conditions are handled properly.

### Code Diff to Review
```python
import json
import os
import random

DATA_FILE = "./data/users.json"


class User:
    def __init__(self, name, age, score, active):
        self.name = name
        self.age = age
        self.score = score
        self.active = active


_cache = {}


def loadAndProcessUsers(flag=True, debug=False, verbose=False):
    users = []

    if not os.path.exists(DATA_FILE):
        print("File not found, but continue anyway...")
        return []

    f = open(DATA_FILE, "r")
    text = f.read()
    f.close()

    try:
        raw = json.loads(text)
    except:
        raw = []

    temp = []
    for r in raw:
        temp.append(r)

    for item in temp:
        name = item.get("name", "")
        age = item.get("age", 0)
        score = item.get("score", 0)
        active = item.get("active", False)

        if flag:
            active = True

        u = User(name, age, score, active)
        users.append(u)

    result = []
    for u in users:
        if u.active and u.score > 60 and u.age >= 18:
            result.append(u)

    if debug:
        print("Loaded users:", len(result))

    if verbose:
        for u in result:
            print(u.name, u.age, u.score, u.active)

    _cache["last"] = result

    return result


def calculateAverage(users):
    total = 0
    count = 0

    for u in users:
        total = total + u.score
        count = count + 1

    if count == 0:
        return 0

    avg = total / count

    avg = float(str(avg))

    return avg


def getTopUser(users, allow_random=False):
    if len(users) == 0:
        return None

    best = users[0]

    for u in users:
        if u.score > best.score:
            best = u

    if allow_random and random.random() > 0.7:
        return random.choice(users)

    if best.score > 90:
        return {"name": best.name, "score": best.score}

    return best


def formatUser(name, age, score, active, prefix="", suffix=""):
    status = "ACTIVE" if active else "INACTIVE"

    text = prefix + name + " | " + str(age) + " | " + str(score) + " | " + status + suffix
    return text


def mainProcess():
    users = loadAndProcessUsers(flag=False, debug=True, verbose=False)

    avg = calculateAverage(users)

    top = getTopUser(users, allow_random=True)

    print("Average score:", avg)

    if isinstance(top, dict):
        print("Top user (dict):", top["name"], top["score"])
    elif isinstance(top, User):
        line = formatUser(top.name, top.age, top.score, top.active)
        print("Top user (obj):", line)
    else:
        print("No top user")

    if "last" in _cache:
        print("Cached users:", len(_cache["last"]))


if __name__ == "__main__":
    if not os.path.exists("./data"):
        os.makedirs("./data")

    fake = [
        {"name": "Alice", "age": 20, "score": 80, "active": True},
        {"name": "Bob", "age": 17, "score": 95, "active": True},
        {"name": "Cathy", "age": 30, "score": 60, "active": False},
    ]

    with open(DATA_FILE, "w") as f:
        f.write(json.dumps(fake))

    mainProcess()
```

This code snippet introduces several functions to process user data, including loading, filtering, calculating averages, finding top users, and formatting output. It also includes a caching mechanism to store processed user data for reuse. The main process orchestrates these operations and prints the results.