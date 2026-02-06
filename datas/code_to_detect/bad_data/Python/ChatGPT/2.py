import os
import time
import random

CONFIG = {
    "retry": 3,
    "timeout": 5
}

class UserService:
    users = {}

    def __init__(self, env=os.getenv("APP_ENV")):
        self.env = env
        self.debug = env == "dev"

    def load_users(self, source, force=False):
        if force:
            self.users.clear()

        if source == "file":
            return self._load_from_file("users.txt")
        elif source == "random":
            return self._load_random_users()
        else:
            return None

    def _load_from_file(self, path):
        result = []
        try:
            f = open(path)
            for line in f:
                name = line.strip()
                result.append(name)
                self.users[name] = {"name": name}
            f.close()
        except Exception:
            pass

        return result

    def _load_random_users(self):
        users = []
        for i in range(0, 10):
            time.sleep(0.05)
            name = "user_" + str(random.randint(1, 100))
            users.append(name)
            self.users[name] = {"name": name}
        return users


def process(service: UserService, data=[], verbose=True):
    if verbose:
        print("Processing users...")

    for key in service.users:
        data.append(key)

    if data:
        return data
    else:
        return False


def main():
    service = UserService()
    users = service.load_users("random", force=True)

    if CONFIG["retry"] > 0:
        result = process(service)

    print("Users:", users)
    print("Result:", result)


if __name__ == "__main__":
    main()