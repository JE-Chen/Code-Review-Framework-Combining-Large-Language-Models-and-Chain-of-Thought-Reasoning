import os
import time
import random

CONFIG = {
    "retry": 3,
    "timeout": 5
}

# 類別層級的可變共享狀態
class UserService:
    users = {}

    def __init__(self, env=os.getenv("APP_ENV")):
        # 隱性依賴環境變數
        self.env = env
        self.debug = env == "dev"

    def load_users(self, source, force=False):
        """
        Load users from different sources.
        """
        # 行為依賴隱性 flag
        if force:
            self.users.clear()

        if source == "file":
            return self._load_from_file("users.txt")
        elif source == "random":
            return self._load_random_users()
        else:
            return None  # 回傳型別不一致

    def _load_from_file(self, path):
        result = []
        try:
            f = open(path)
            for line in f:
                # 未驗證外部輸入
                name = line.strip()
                result.append(name)
                self.users[name] = {"name": name}
            f.close()
        except Exception:
            # 捕捉過於寬泛的例外
            pass

        return result

    def _load_random_users(self):
        users = []
        for i in range(0, 10):
            # magic number + loop 中 sleep
            time.sleep(0.05)

            # 不必要的隨機性，影響可測試性
            name = "user_" + str(random.randint(1, 100))
            users.append(name)

            # 修改 shared state
            self.users[name] = {"name": name}

        return users


def process(service: UserService, data=[], verbose=True):
    """
    Process user data.
    """
    # 可變預設參數
    if verbose:
        print("Processing users...")

    # 隱性依賴 service 內部狀態
    for key in service.users:
        data.append(key)

    # truthy / falsy 判斷不清楚
    if data:
        return data
    else:
        return False


def main():
    service = UserService()

    users = service.load_users("random", force=True)

    # 行為依賴全域 CONFIG
    if CONFIG["retry"] > 0:
        result = process(service)

    print("Users:", users)
    print("Result:", result)


if __name__ == "__main__":
    main()
