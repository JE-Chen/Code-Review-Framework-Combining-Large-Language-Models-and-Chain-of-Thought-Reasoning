### Title: Data Processing Script Using External API

### Overview
This script fetches user, post, and comment data from a public JSONPlaceholder API and processes this data to identify special users, long post titles, and emails containing '@'. The processed results are then printed.

### Detailed Explanation
1. **Constants**:
   - `BASE_URL`: Base URL of the JSONPlaceholder API.
   - `HEADERS`: Headers specifying the content type as JSON.
   - `GLOBAL_RESULTS`: A global list to store processed results.

2. **Functions**:
   - `get_users()`: Fetches user data from the API.
   - `get_posts()`: Fetches post data from the API.
   - `get_comments()`: Fetches comment data from the API.
   - `process_data()`: Processes fetched data to identify specific patterns.
   - `main()`: Orchestrates the workflow, calls other functions, and prints results.

3. **Processing Logic**:
   - Iterates through users, posts, and comments.
   - Checks conditions and appends matching items to `GLOBAL_RESULTS`.

4. **Output**:
   - Prints each result stored in `GLOBAL_RESULTS`.
   - Provides a summary based on the number of results.

### Assumptions & Edge Cases
- Assumes internet connectivity to access the external API.
- Handles exceptions gracefully but doesn't retry failed requests.
- No assumptions about the structure of the JSON responses beyond basic keys.

### Possible Errors
- Network issues causing requests to fail.
- Invalid JSON responses from the API.

### Performance & Security Concerns
- Minimal performance impact due to small datasets.
- Potential security risks if handling sensitive data without proper validation.

### Suggested Improvements
1. **Logging**: Replace print statements with logging for better control over output levels.
2. **Retry Mechanism**: Implement retries for transient failures.
3. **Data Validation**: Validate JSON responses before processing.
4. **Asynchronous Requests**: Use asynchronous requests for better performance with large datasets.

### Example Usage
```python
# This is the entry point of the script
if __name__ == "__main__":
    main()
```
When run, the script will fetch data, process it, and print the results along with a summary.