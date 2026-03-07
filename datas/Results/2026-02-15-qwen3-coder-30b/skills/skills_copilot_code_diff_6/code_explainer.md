# HTTP Request Handler with Poor Error Handling

## Overview
This Python script makes three HTTP requests using the `requests` library to a public JSON API endpoint, but suffers from poor design practices including global state, ambiguous naming, and inadequate error handling.

## Detailed Explanation

### Flow and Components
- **Global State**: Uses `GLOBAL_SESSION` (a requests.Session object) and `ANOTHER_GLOBAL` constant throughout the module
- **Main Function** (`functionThatDoesTooMuchAndIsHardToUnderstand`):
  1. Makes GET request to `/posts/1` endpoint
  2. Prints status code and raw response text
  3. Makes second GET request to `/posts` endpoint 
  4. Checks if second request succeeded and prints data length
  5. Makes POST request to create new post
  6. Prints POST response text
- **Error Handling**: Catches all exceptions but ignores them completely
- **Hardcoded URLs**: All endpoints are hardcoded strings

### Key Issues Identified
- **Function Responsibilities**: Single function handles multiple unrelated operations
- **Naming Convention**: Unclear variable/function names make code hard to understand
- **Exception Handling**: Generic exception catching without proper logging or recovery
- **Global Variables**: Pollutes namespace and creates tight coupling
- **No Input Validation**: No parameterization or configuration management

## Improvements
1. **Separate Concerns**: Split functionality into distinct functions per operation
2. **Better Variable Names**: Use descriptive names instead of cryptic ones
3. **Specific Exception Handling**: Catch specific exceptions rather than generic `Exception`
4. **Remove Global State**: Pass dependencies explicitly instead of relying on globals
5. **Add Configuration Management**: Externalize URLs and settings
6. **Proper Logging**: Replace print statements with structured logging
7. **Return Values**: Functions should return results instead of just printing

## Example Usage
```python
# Current behavior - runs all requests sequentially with no input parameters
# Would output various status codes, response texts, and lengths
```

The script demonstrates anti-patterns common in hastily written integration code that should be refactored before production use.