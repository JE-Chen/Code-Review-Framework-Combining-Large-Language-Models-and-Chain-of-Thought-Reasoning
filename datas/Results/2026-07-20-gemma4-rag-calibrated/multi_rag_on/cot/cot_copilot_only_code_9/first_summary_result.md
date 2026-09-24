### Code Review

#### 1. Readability & Consistency
- **Formatting:** The code is generally well-formatted, but the nested `if/else` blocks in `main()` are unnecessarily deep, reducing readability.

#### 2. Naming Conventions
- **Variable Names:** In `process_data()`, the loop variables `u`, `p`, and `c` are too concise. They should be renamed to `user`, `post`, and `comment` to maintain semantic clarity.

#### 3. Software Engineering Standards
- **Code Duplication:** The functions `get_users`, `get_posts`, and `get_comments` are nearly identical. This is a violation of the DRY (Don't Repeat Yourself) principle.
    - *Recommendation:* Create a generic `fetch_data(endpoint)` function to handle the request and exception logic.
- **Modularity:** The use of `GLOBAL_RESULTS` as a global list makes the code harder to test and maintain.
    - *Recommendation:* `process_data()` should return a list of results, which `main()` can then pass to a printing function.

#### 4. Logic & Correctness
- **Potential Crash:** In `process_data()`, the code uses `p["title"]` and `c["email"]` after checking for their existence using `.get()`. If the key is missing, the `.get()` check passes (returning an empty string), but the subsequent direct access `p["title"]` will raise a `KeyError`.
    - *Recommendation:* Use the variable captured by `.get()` or ensure the key exists before direct access.
- **Exception Handling:** Catching a generic `Exception` is too broad. It should specifically target `requests.exceptions.RequestException`.

#### 5. Performance & Security
- **Network Efficiency:** The three API calls are performed sequentially. While acceptable for this scale, they could be performed concurrently if performance becomes a bottleneck.

#### 6. Documentation & Testing
- **Missing Tests:** There are no unit tests provided to verify the filtering logic in `process_data`.

---

### PR Summary

**Key Changes**
- Implemented a data retrieval and filtering pipeline that fetches users, posts, and comments from an external API.
- Added logic to filter specific users, long post titles, and valid comment emails.

**Purpose of Changes**
- Feature addition: Establish a basic data processing flow for the JSONPlaceholder API.

**Items to Confirm**
- Review the error handling in the `get_*` functions.
- Validate the filtering criteria used in `process_data`.