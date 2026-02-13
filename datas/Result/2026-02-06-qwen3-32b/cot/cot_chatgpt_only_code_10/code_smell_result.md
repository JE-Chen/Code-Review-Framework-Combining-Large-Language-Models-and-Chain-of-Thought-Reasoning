Code Smell Type: Unintended Header Overwrite  
Problem Location:  
```python
headers["User-Agent"] = "BadClient/1.0"
```  
in `fetch_resource` function.  
Detailed Explanation: The function unconditionally overrides the `User-Agent` header, preventing callers from customizing it. This violates the principle of least surprise and creates hidden coupling. Callers cannot use their preferred User-Agent (e.g., for mobile testing), and the hardcoded value ("BadClient/1.0") is unprofessional and non-configurable.  
Improvement Suggestions: Remove the hardcoded assignment. Instead, document that callers *must* provide a `User-Agent` header via `headers` parameter. If a default is needed, use a separate configuration mechanism.  
Priority Level: High  

---

Code Smell Type: Hidden State and Caching  
Problem Location:  
```python
if not hasattr(fetch_resource, "cache"):
    fetch_resource.cache = {}
```  
in `fetch_resource` function.  
Detailed Explanation: The cache is stored as a module-level attribute on the function object, creating hidden state. This causes multiple issues:  
- Non-thread-safe (race conditions in concurrent use)  
- Memory leak (cache never cleared, grows indefinitely)  
- Impossible to reset or mock for testing  
- Violates single responsibility (caching logic mixed with HTTP handling)  
Improvement Suggestions: Inject cache as a dependency (e.g., `cache: dict = {}`). Use a dedicated `Cache` class or dependency injection framework. Remove cache from the function signature and handle it externally.  
Priority Level: High  

---

Code Smell Type: Shadowing Built-in Function  
Problem Location:  
```python
def hash(text):
```  
Detailed Explanation: The function name `hash` conflicts with Python's built-in `hash()` function. This shadows the built-in, causing subtle bugs if callers accidentally use `hash()` instead of the custom function (e.g., `hash = ...` followed by `hash(obj)`). It also reduces readability.  
Improvement Suggestions: Rename to `compute_md5_hash` or `get_md5_checksum`.  
Priority Level: Medium  

---

Code Smell Type: Magic Numbers and Hardcoded Values  
Problem Location:  
```python
chunk_size=1234
```  
and  
```python
if preview and len(content) > 3000:
```  
in `download_file` function.  
Detailed Explanation: The numbers `1234` and `3000` are arbitrary without context. They make the code brittle (e.g., changing the preview limit requires editing multiple locations) and obscure intent.  
Improvement Suggestions: Define constants:  
```python
DEFAULT_CHUNK_SIZE = 1234
PREVIEW_SIZE_LIMIT = 3000
```  
Use these in the function.  
Priority Level: Low  

---

Code Smell Type: Missing Error Handling  
Problem Location:  
All network-related functions (`fetch_resource`, `download_file`, `wait_until_ready`).  
Detailed Explanation: No exception handling for network failures (e.g., `requests.exceptions.RequestException`). This causes unhandled crashes on timeouts, DNS errors, or 5xx responses. Critical for production resilience.  
Improvement Suggestions: Add retry logic (e.g., `tenacity` library) and meaningful error messages. Example:  
```python
try:
    r = requests.get(...)
except requests.exceptions.RequestException as e:
    raise ServiceUnavailableError(f"Failed to fetch {url}") from e
```  
Priority Level: High  

---

Code Smell Type: Side Effects in Non-Logging Functions  
Problem Location:  
```python
print("Request headers:", r.request.headers)
```  
in `fetch_and_verify`.  
Detailed Explanation: The function prints to stdout as a side effect. This violates separation of concerns: the function should return data, not handle I/O. Makes unit testing impossible and pollutes logs.  
Improvement Suggestions: Remove the print statement. Let the caller handle logging.  
Priority Level: Medium  

---

Code Smell Type: Unvalidated Input Parameter  
Problem Location:  
```python
def fetch_and_verify(url, delay=0.0):
```  
Detailed Explanation: `delay` can be negative (e.g., `delay=-1.0`), causing `time.sleep(-1.0)` to fail. No input validation.  
Improvement Suggestions: Add validation:  
```python
if delay < 0:
    raise ValueError("delay must be non-negative")
```  
Priority Level: Medium