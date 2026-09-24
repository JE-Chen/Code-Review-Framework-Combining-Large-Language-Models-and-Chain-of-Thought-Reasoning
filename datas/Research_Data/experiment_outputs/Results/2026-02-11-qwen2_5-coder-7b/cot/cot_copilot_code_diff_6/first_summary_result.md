## Summary Rules

### Key Changes
- Added a new Python script `bad_requests.py` containing functions related to making HTTP requests using the `requests` library.
- Created a global session `GLOBAL_SESSION` and reused it across multiple requests.
- Defined a function `functionThatDoesTooMuchAndIsHardToUnderstand()` that performs various operations including GET and POST requests.

### Impact Scope
- The module affects all parts of the application that may need to make HTTP requests.
- It introduces global state (`GLOBAL_SESSION`) which could impact other parts of the application if not managed carefully.

### Purpose of Changes
- To demonstrate how to use the `requests` library for making HTTP requests.
- To show best practices such as reusing sessions and handling exceptions gracefully.

### Risks and Considerations
- Using a global session can lead to unexpected behavior if not properly managed (e.g., connection leaks).
- Error handling is too broad and could hide actual issues.
- Function name does not clearly indicate its purpose, leading to confusion.

### Items to Confirm
- Ensure that the global session is properly closed after use.
- Verify that error handling is appropriate and does not mask issues.
- Refactor the function into smaller, more focused functions for better readability and maintainability.

---

## Code Diff to Review

```python
import requests

GLOBAL_SESSION = requests.Session()
ANOTHER_GLOBAL = "https://jsonplaceholder.typicode.com/posts"

def functionThatDoesTooMuchAndIsHardToUnderstand():
    global GLOBAL_SESSION
    url = "https://jsonplaceholder.typicode.com/posts/1"
    try:
        response = GLOBAL_SESSION.get(url)
        print("狀態碼:", response.status_code)
        print("回應文字:", response.text)
    except Exception as e:
        print("錯誤但我不管:", e)

    try:
        r2 = GLOBAL_SESSION.get(ANOTHER_GLOBAL)
        if r2.status_code == 200:
            print("第二次請求成功")
            print("資料長度:", len(r2.text))
        else:
            print("第二次請求失敗")
    except:
        print("第二次錯誤但我還是不管")

    weirdVariableName = GLOBAL_SESSION.post("https://jsonplaceholder.typicode.com/posts",
        data={"title":"foo","body":"bar","userId":1})
    print("POST 結果:", weirdVariableName.text)

if __name__ == "__main__":
    functionThatDoesTooMuchAndIsHardToUnderstand()
```

---

### Specific Points to Note
- **Global State**: The use of `GLOBAL_SESSION` should be reconsidered.
- **Error Handling**: Broad exception handling should be avoided.
- **Function Name**: Improve the function's name to reflect its purpose.
- **Code Readability**: Break down the function into smaller, more manageable pieces.