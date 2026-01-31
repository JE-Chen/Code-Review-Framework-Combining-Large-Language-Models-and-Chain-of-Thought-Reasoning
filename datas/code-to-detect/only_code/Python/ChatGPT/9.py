# Python requests 範例程式碼：能執行但充滿程式碼異味
# 程式碼異味包含：過度使用 Session、不必要的封裝、結構混亂、錯誤處理不足、魔法字串與數字

import requests

# 全域 Session 濫用
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "CodeSmellBot/1.0"})

BASE_URL = "https://jsonplaceholder.typicode.com"
GLOBAL_CACHE = {}

class APIClient:
    # 過度封裝：其實不需要類別
    def __init__(self, base_url):
        self.base_url = base_url

    def fetch(self, endpoint):
        # 過度複雜的邏輯，沒有抽象化
        try:
            url = self.base_url + endpoint
            response = SESSION.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": "Bad status: " + str(response.status_code)}
        except Exception as e:
            # 過度廣泛的例外攔截
            return {"error": str(e)}

def get_users(client):
    # 重複邏輯：每個函式都自己呼叫 fetch
    data = client.fetch("/users")
    GLOBAL_CACHE["users"] = data
    return data

def get_posts(client):
    data = client.fetch("/posts")
    GLOBAL_CACHE["posts"] = data
    return data

def get_todos(client):
    data = client.fetch("/todos")
    GLOBAL_CACHE["todos"] = data
    return data

def process_all():
    # 過度複雜的邏輯，硬塞在一個函式裡
    client = APIClient(BASE_URL)
    users = get_users(client)
    posts = get_posts(client)
    todos = get_todos(client)

    results = []
    for u in users:
        if u.get("id") == 1:  # 魔法數字
            results.append("Special User: " + u.get("name", "Unknown"))

    for p in posts:
        if len(p.get("title", "")) > 15:  # 魔法數字
            results.append("Long Post: " + p["title"])

    for t in todos:
        if not t.get("completed", False):
            results.append("Incomplete Todo: " + t.get("title", "No Title"))

    return results

def main():
    results = process_all()
    for r in results:
        print("Result:", r)

    # 過度巢狀的邏輯
    if len(results) > 0:
        if len(results) < 5:
            print("Few results")
        else:
            if len(results) < 20:
                print("Moderate results")
            else:
                print("Too many results")
    else:
        print("No results found")

if __name__ == "__main__":
    main()