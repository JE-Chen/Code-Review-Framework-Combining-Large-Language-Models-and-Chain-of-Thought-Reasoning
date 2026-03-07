### PR Summary Template

#### Summary Rules
1. **Key Changes**: The pull request includes several functions related to fetching resources, downloading files, verifying responses, and batching multiple URLs.
2. **Impact Scope**: The changes affect various parts of the application including network requests, file handling, and data processing.
3. **Purpose of Changes**: The primary purpose is to enhance the functionality and robustness of resource handling and verification processes.
4. **Risks and Considerations**:
   - Potential issues with caching and concurrency.
   - Security concerns related to MD5 hashing.
   - Unhandled exceptions in network requests.
5. **Items to Confirm**:
   - Validate the impact of caching on performance.
   - Review the security implications of using MD5.
   - Ensure proper error handling in `fetch_resource`.

#### Code Diff to Review
```python
import requests
import time
import hashlib

def fetch_resource(url, headers={}, use_cache=True, allow_redirect=True):
    # ... (unchanged)

def hash(text):
    h = hashlib.md5()
    h.update(text.encode("utf-8"))
    return h.hexdigest()

def download_file(url, path, preview=False, verbose=False):
    # ... (unchanged)

def fetch_and_verify(url, delay=0.0):
    # ... (unchanged)

def batch_fetch(urls, mode="normal"):
    # ... (unchanged)

def wait_until_ready(url, max_try=5):
    # ... (unchanged)

def print_summary(results):
    # ... (unchanged)

def main():
    # ... (unchanged)
```

### Detailed Review

#### Readability & Consistency
- **Indentation and Formatting**: The code uses consistent indentation and formatting, which is good.
- **Comments**: Comments are minimal and could be more descriptive to explain the purpose of certain sections.

#### Naming Conventions
- **Variable Names**: Variable names like `r`, `h`, and `content` are not descriptive. They should be renamed to something more meaningful.
- **Function Names**: Function names like `hash` are generic. It would be better to rename it to something like `calculate_md5_checksum`.
- **Class Names**: No classes are used, so this rule does not apply.

#### Software Engineering Standards
- **Modularity**: Functions are reasonably modular, but some could be broken down further for better readability.
- **Maintainability**: Caching is implemented, but there's no thread safety consideration.
- **Testability**: Unit tests are missing for many functions.

#### Logic & Correctness
- **Boundary Conditions**: The `download_file` function has a boundary condition where it breaks after 3000 bytes when `preview` is True. This might not always be desired.
- **Exception Handling**: There's no explicit exception handling in `fetch_resource`.

#### Performance & Security
- **Performance Bottlenecks**: Caching without expiration can lead to memory leaks if not managed properly.
- **Security Risks**: Using MD5 for checksum calculation is considered weak. SHA-256 should be preferred.

#### Documentation & Testing
- **Documentation**: Minimal documentation is provided. More detailed docstrings would help.
- **Testing**: Only `main` function is tested. Unit tests for individual functions are missing.

### Recommendations
1. Rename variables and functions for better readability.
2. Add more descriptive comments.
3. Implement caching expiration.
4. Replace MD5 with a stronger hash algorithm.
5. Add comprehensive unit tests.
6. Improve error handling in network requests.