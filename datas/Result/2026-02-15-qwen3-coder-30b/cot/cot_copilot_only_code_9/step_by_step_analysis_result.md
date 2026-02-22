### 1. **Global Variable Usage**
- **Issue**: Using `GLOBAL_RESULTS` as a global variable reduces modularity and makes testing difficult.
- **Explanation**: When a function modifies a global variable, its behavior depends on external state, which is hard to predict and test.
- **Why It Happens**: Design choice to accumulate results globally instead of returning them explicitly.
- **Risk**: Side effects increase risk of bugs, especially under concurrent execution or during testing.
- **Fix**: Pass results into or out of functions; avoid mutating shared state.
    ```python
    # Before
    def process_data():
        GLOBAL_RESULTS.append(...)

    # After
    def process_data(results):
        return results + [...]
    ```

---

### 2. **Duplicate HTTP Request Logic**
- **Issue**: `get_users`, `get_posts`, and `get_comments` all have repeated HTTP request code.
- **Explanation**: Copy-pasted logic leads to inconsistencies and maintenance overhead.
- **Why It Happens**: Lack of abstraction for common API interaction patterns.
- **Risk**: One update won’t propagate to other similar functions.
- **Fix**: Extract common logic into a reusable helper.
    ```python
    def fetch_api_data(endpoint):
        try:
            response = requests.get(f"{BASE_URL}/{endpoint}")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching {endpoint}: {e}")
            return None
    ```

---

### 3. **Catch Generic Exception**
- **Issue**: `except Exception` catches too many types of errors.
- **Explanation**: Masks real problems and hides debugging clues.
- **Why It Happens**: Broad exception handling used for simplicity or lack of understanding.
- **Risk**: Silent failures or misinterpretation of failure modes.
- **Fix**: Catch specific exceptions like `requests.RequestException`.
    ```python
    # Before
    except Exception as e:

    # After
    except requests.RequestException as e:
    ```

---

### 4. **Magic Numbers & Strings**
- **Issue**: Hardcoded values like `10`, `50`, and `"Special User"` reduce clarity.
- **Explanation**: Readers must guess meaning behind numbers or strings.
- **Why It Happens**: Quick prototyping without considering long-term readability.
- **Risk**: Changes require updating multiple locations.
- **Fix**: Replace with named constants.
    ```python
    MIN_USERS_THRESHOLD = 10
    MAX_POSTS_THRESHOLD = 50
    SPECIAL_USER_LABEL = "Special User"
    ```

---

### 5. **Print Instead of Logging**
- **Issue**: Direct use of `print()` instead of logging.
- **Explanation**: Makes output management and filtering impossible in production.
- **Why It Happens**: Convenience over scalability.
- **Risk**: No control over verbosity or format in deployments.
- **Fix**: Switch to logging module.
    ```python
    import logging
    logging.info("Processing data...")
    ```

---

### 6. **Hardcoded URLs**
- **Issue**: Base URL is hardcoded, making configuration hard.
- **Explanation**: Changing endpoints requires code edits.
- **Why It Happens**: Ignoring environment-specific setups.
- **Risk**: Deployment issues due to hardcoding.
- **Fix**: Externalize via environment variables or config files.
    ```python
    import os
    BASE_URL = os.getenv("API_BASE_URL", "https://api.example.com")
    ```

--- 

### Summary of Best Practices Applied:
- Avoid global state.
- Eliminate duplication with helpers.
- Prefer specific exceptions.
- Use constants for magic values.
- Prefer structured logging.
- Externalize configuration.

By addressing these points, your code will become more modular, readable, and maintainable.