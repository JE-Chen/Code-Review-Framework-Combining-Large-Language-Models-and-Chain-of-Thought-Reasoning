Title: Code Review of `bad_requests.py`

Overview:
This Python script demonstrates several bad practices in handling HTTP requests, including global state, exception handling, and unclear functionality.

Detailed Explanation:

1. **Imports and Global Variables**
   - The script imports the `requests` library.
   - It defines two global variables: `GLOBAL_SESSION`, which is a session object from the `requests` library, and `ANOTHER_GLOBAL`, which holds a URL string.

2. **Function: `functionThatDoesTooMuchAndIsHardToUnderstand()`**
   - This function performs multiple unrelated tasks without clear separation of concerns.
   - It makes three separate HTTP GET and POST requests.
   - It uses a global session to reuse connections between requests.
   - It handles exceptions but ignores them instead of logging or re-raising them.

3. **HTTP Requests**
   - The function makes a GET request to fetch a specific post (`posts/1`) and prints its status code and text.
   - It then makes another GET request to fetch all posts and checks if the response was successful.
   - Finally, it sends a POST request with form data and prints the response text.

4. **Exception Handling**
   - The function catches exceptions but simply prints an error message without any action taken.

5. **Naming Conventions**
   - Variable names like `weirdVariableName` do not follow PEP 8 naming conventions, making the code harder to read.

Improvements:

1. **Separate Functions for Each Task**
   - Break down the function into smaller, single-purpose functions that handle individual HTTP requests and their responses.

2. **Avoid Global State**
   - Use local variables within functions instead of relying on global variables.

3. **Proper Exception Handling**
   - Log or re-raise exceptions instead of ignoring them.

4. **Use Meaningful Variable Names**
   - Choose variable names that reflect their purpose.

Example Usage:

```python
# Assuming each task is handled by a separate function

def fetch_post(post_id):
    # Fetch a specific post using a new session
    response = requests.get(f"https://jsonplaceholder.typicode.com/posts/{post_id}")
    return response.json()

def fetch_all_posts():
    # Fetch all posts using a new session
    response = requests.get("https://jsonplaceholder.typicode.com/posts")
    return response.json()

def create_post(data):
    # Create a new post using a new session
    response = requests.post("https://jsonplaceholder.typicode.com/posts", json=data)
    return response.json()

# Usage
post = fetch_post(1)
all_posts = fetch_all_posts()
new_post = create_post({"title": "foo", "body": "bar", "userId": 1})
```

This refactored version separates concerns, avoids global state, and provides clearer function responsibilities.