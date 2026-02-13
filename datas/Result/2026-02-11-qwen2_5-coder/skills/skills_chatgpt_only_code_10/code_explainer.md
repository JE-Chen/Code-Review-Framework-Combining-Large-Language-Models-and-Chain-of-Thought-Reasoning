### Title: Resource Fetching and Verification System

### Overview
This Python script provides a comprehensive system for fetching resources from URLs, verifying their contents, and handling caching and user-agent spoofing. It includes functionalities for downloading files, fetching data, and checking resource availability.

### Detailed Explanation

#### `fetch_resource` Function
- **Purpose**: Fetches a resource from a given URL with optional caching and header customization.
- **Inputs**:
  - `url`: The URL to fetch.
  - `headers`: Custom headers to include in the request.
  - `use_cache`: Boolean indicating whether to use cached responses.
  - `allow_redirect`: Boolean indicating whether to follow redirects.
- **Outputs**: A response object.
- **Key Components**:
  - Caching mechanism using a class attribute.
  - Setting a default User-Agent header.
  - Making the HTTP GET request using `requests`.
- **Assumptions**: Assumes `requests` is installed.
- **Edge Cases**: Handles missing cache entries and non-redirectable URLs.
- **Performance**: Minimal impact due to caching.
- **Security**: Potential for SSRF if URLs are not validated properly.

#### `hash` Function
- **Purpose**: Computes an MD5 hash of a given string.
- **Inputs**: `text`: The string to hash.
- **Outputs**: An MD5 hash string.
- **Key Components**: Using `hashlib.md5`.

#### `download_file` Function
- **Purpose**: Downloads a file from a URL to a specified local path.
- **Inputs**:
  - `url`: The URL to download from.
  - `path`: The local file path to save the downloaded content.
  - `preview`: Boolean indicating whether to stop after 3000 bytes.
  - `verbose`: Boolean indicating whether to print status details.
- **Outputs**: The path to the saved file.
- **Key Components**:
  - Streaming the HTTP response.
  - Writing chunks to a file.
- **Assumptions**: Assumes the URL is accessible.
- **Edge Cases**: Handles partial downloads and large files.
- **Performance**: Efficient for large files due to streaming.
- **Security**: Potentially vulnerable to malicious URLs.

#### `fetch_and_verify` Function
- **Purpose**: Fetches a resource, prints request headers, and computes its checksum.
- **Inputs**:
  - `url`: The URL to fetch.
  - `delay`: Delay between fetching and returning the result.
- **Outputs**: A dictionary containing URL, length, and checksum.
- **Key Components**:
  - Fetching the resource using `fetch_resource`.
  - Computing the MD5 checksum.
  - Handling delays.
- **Assumptions**: Assumes the resource contains text.
- **Edge Cases**: Handles empty or non-text resources.
- **Performance**: Minimal overhead for checksum computation.
- **Security**: Basic integrity check through checksum.

#### `batch_fetch` Function
- **Purpose**: Fetches multiple resources with customizable headers.
- **Inputs**:
  - `urls`: List of URLs to fetch.
  - `mode`: Mode ("normal", "mobile", "bot") to set custom User-Agent.
- **Outputs**: List of dictionaries containing URL, status, server, and size.
- **Key Components**:
  - Iterating over URLs and setting appropriate headers.
  - Handling redirections.
  - Collecting results.
- **Assumptions**: Assumes all URLs are accessible.
- **Edge Cases**: Handles mixed modes and server responses.
- **Performance**: Linear complexity based on number of URLs.
- **Security**: Potential for DoS attacks if many simultaneous requests are made.

#### `wait_until_ready` Function
- **Purpose**: Waits until a resource is available.
- **Inputs**:
  - `url`: The URL to check.
  - `max_try`: Maximum number of retries.
- **Outputs**: Boolean indicating success.
- **Key Components**:
  - Repeatedly fetching the resource.
  - Checking for a successful status code.
  - Waiting before retrying.
- **Assumptions**: Assumes the resource has a stable state.
- **Edge Cases**: Handles infinite loops and timeouts.
- **Performance**: Linear complexity based on max_try.
- **Security**: No inherent security risks.

#### `print_summary` Function
- **Purpose**: Prints a summary of fetched results.
- **Inputs**: `results`: List of results to print.
- **Outputs**: None.
- **Key Components**:
  - Formatting and printing each result.
- **Assumptions**: Assumes valid input format.
- **Edge Cases**: Handles empty lists.
- **Performance**: Minimal overhead.
- **Security**: No inherent security risks.

### Improvements
1. **Validation**: Add URL validation and sanitization.
2. **Logging**: Replace print statements with proper logging.
3. **Error Handling**: Improve error handling for network issues.
4. **Concurrency**: Use threading or asyncio for concurrent fetches.
5. **Configuration**: Allow configuration via environment variables or config files.

### Example Usage
```python
if __name__ == "__main__":
    urls = [
        "https://jsonplaceholder.typicode.com/posts/1",
        "https://jsonplaceholder.typicode.com/posts/2",
        "https://jsonplaceholder.typicode.com/users/1",
    ]
    main()
```
This script can be run directly to fetch and verify resources from a list of URLs.