Sure, let's analyze each lint message and code smell step-by-step:

### 1. Global Variables
#### Problem Location
```python
GLOBAL_SESSION = requests.Session()
ANOTHER_GLOBAL = "https://jsonplaceholder.typicode.com/posts"
```
#### Detailed Explanation
The use of global variables (`GLOBAL_SESSION` and `ANOTHER_GLOBAL`) can lead to issues such as unexpected side effects when multiple parts of the application modify these globals. It also makes the dependencies of functions unclear, making the code harder to reason about and test.

#### Improvement Suggestions
Pass the session object as an argument to functions instead of using a global variable. This improves encapsulation and testability.
```python
def fetch_data(session, url):
    return session.get(url)

# Usage
session = requests.Session()
data = fetch_data(session, "https://jsonplaceholder.typicode.com/posts")
```
#### Priority Level
High

### 2. Print Statements
#### Problem Location
```python
print("第二次錯誤但我還是不管")
```
#### Detailed Explanation
Using print statements for debugging is discouraged in production code. Consider using logging instead.

#### Improvement Suggestions
Replace `print` with `logging.info`, `logging.error`, etc.
```python
import logging

logging.basicConfig(level=logging.ERROR)
logging.error("第二次錯誤但我還是不管")
```
#### Priority Level
Error

### 3. General Exception Handling
#### Problem Location
```python
except:
    print("第二次錯誤但我還是不管")
```
#### Detailed Explanation
Catching all exceptions (`except:`) without specifying the exception type catches all exceptions, including system-exiting exceptions.

#### Improvement Suggestions
Catch specific exceptions and handle them gracefully.
```python
try:
    # Some code that might raise an exception
    pass
except SomeSpecificException as e:
    logging.error(f"Caught exception: {e}")
```
#### Priority Level
Error

### 4. Variable Naming
#### Problem Location
```python
weirdVariableName = GLOBAL_SESSION.post(...)
```
#### Detailed Explanation
Variable name `weirdVariableName` does not follow naming conventions.

#### Improvement Suggestions
Use a more descriptive name that reflects the variable's purpose.
```python
response = GLOBAL_SESSION.post(...)
```
#### Priority Level
Warning

By addressing these issues, you can improve the maintainability, readability, and robustness of your code.