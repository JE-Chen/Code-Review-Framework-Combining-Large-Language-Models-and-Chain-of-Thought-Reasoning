import requests

BASE_URL = "https://jsonplaceholder.typicode.com"
HEADERS = {"Content-Type": "application/json"}
GLOBAL_RESULTS = []

def get_users():
    try:
        response = requests.get(BASE_URL + "/users", headers=HEADERS)
        return response.json()
    except Exception as e:
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
    users = get_users()
    posts = get_posts()
    comments = get_comments()

    for u in users:
        if u.get("id") == 5:
            GLOBAL_RESULTS.append("Special User: " + u.get("name", "Unknown"))

    for p in posts:
        if len(p.get("title", "")) > 20:
            GLOBAL_RESULTS.append("Long Post Title: " + p["title"])

    for c in comments:
        if "@" in c.get("email", ""):
            GLOBAL_RESULTS.append("Comment by email: " + c["email"])

def main():
    process_data()
    for r in GLOBAL_RESULTS:
        print("Result:", r)

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