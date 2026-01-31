# Python requests 範例程式碼：能執行但充滿程式碼異味
# 程式碼異味包含：重複程式碼、錯誤處理不足、全域變數濫用、魔法字串與數字、結構混亂

import requests

# 全域變數濫用
BASE_URL = "https://jsonplaceholder.typicode.com"
HEADERS = {"Content-Type": "application/json"}
GLOBAL_RESULTS = []

def get_users():
    # 重複程式碼：每個函式都自己呼叫 requests，沒有抽象化
    try:
        response = requests.get(BASE_URL + "/users", headers=HEADERS)
        return response.json()
    except Exception as e:
        # 過度廣泛的例外攔截
        print("Error in get_users:", e)
        return []

def get_posts():
    try:
        response = requests.get(BASE_URL + "/posts", headers=HEADERS)
        return response.json()
    except Exception as e:
        print("Error in get_posts:", e)
        return []

def get_comments():
    try:
        response = requests.get(BASE_URL + "/comments", headers=HEADERS)
        return response.json()
    except Exception as e:
        print("Error in get_comments:", e)
        return []

def process_data():
    # 過度複雜的邏輯，硬塞在一個函式裡
    users = get_users()
    posts = get_posts()
    comments = get_comments()

    for u in users:
        # 魔法字串與數字
        if u.get("id") == 5:
            GLOBAL_RESULTS.append("Special User: " + u.get("name", "Unknown"))

    for p in posts:
        if len(p.get("title", "")) > 20:  # 魔法數字
            GLOBAL_RESULTS.append("Long Post Title: " + p["title"])

    for c in comments:
        if "@" in c.get("email", ""):  # 魔法字串
            GLOBAL_RESULTS.append("Comment by email: " + c["email"])

def main():
    process_data()
    # 沒有分層設計，直接輸出全域結果
    for r in GLOBAL_RESULTS:
        print("Result:", r)

    # 過度巢狀的邏輯
    if len(GLOBAL_RESULTS) > 0:
        if len(GLOBAL_RESULTS) < 10:
            print("Few results")
        else:
            if len(GLOBAL_RESULTS) < 50:
                print("Moderate results")
            else:
                print("Too many results")
    else:
        print("No results found")

if __name__ == "__main__":
    main()