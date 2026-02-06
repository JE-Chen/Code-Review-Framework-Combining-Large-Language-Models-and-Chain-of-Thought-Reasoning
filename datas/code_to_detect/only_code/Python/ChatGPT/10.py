import requests
import time
import hashlib


def fetch_resource(url, headers={}, use_cache=True, allow_redirect=True):
    if not hasattr(fetch_resource, "cache"):
        fetch_resource.cache = {}

    cache_key = url

    if use_cache and cache_key in fetch_resource.cache:
        return fetch_resource.cache[cache_key]

    headers["User-Agent"] = "BadClient/1.0"

    r = requests.get(
        url,
        headers=headers,
        allow_redirects=allow_redirect
    )

    if use_cache:
        fetch_resource.cache[cache_key] = r

    return r


def hash(text):
    h = hashlib.md5()
    h.update(text.encode("utf-8"))
    return h.hexdigest()


def download_file(url, path, preview=False, verbose=False):
    resp = requests.get(url, stream=True)

    if verbose:
        print("Status:", resp.status_code)
        print("Headers:", resp.headers)

    content = b""

    for chunk in resp.iter_content(chunk_size=1234):
        if preview and len(content) > 3000:
            break
        content += chunk

    with open(path, "wb") as f:
        f.write(content)

    return path


def fetch_and_verify(url, delay=0.0):
    r = fetch_resource(url)

    print("Request headers:", r.request.headers)

    text = r.text

    checksum = hash(text)

    if delay > 0:
        time.sleep(delay)

    return {
        "url": url,
        "length": len(text),
        "checksum": checksum
    }


def batch_fetch(urls, mode="normal"):
    results = []

    headers = {}

    if mode == "mobile":
        headers["User-Agent"] = "iPhone"
    elif mode == "bot":
        headers["User-Agent"] = "GoogleBot"
    else:
        headers["User-Agent"] = "Desktop"

    for u in urls:
        r = fetch_resource(u, headers=headers, use_cache=True)

        if r.history:
            print("Redirected:", u, "->", r.url)

        server = r.headers.get("Server", "unknown")

        results.append({
            "url": u,
            "status": r.status_code,
            "server": server,
            "size": len(r.content)
        })

    return results


def wait_until_ready(url, max_try=5):
    tries = 0

    while tries < max_try:
        r = fetch_resource(url, use_cache=False)

        if r.status_code == 200:
            return True

        time.sleep(1)
        tries += 1

    return False


def print_summary(results):
    print("=== FETCH SUMMARY ===")

    for r in results:
        line = (
            r["url"]
            + " | "
            + str(r["status"])
            + " | "
            + r["server"]
            + " | "
            + str(r["size"])
        )
        print(line)

    return None


def main():
    urls = [
        "https://jsonplaceholder.typicode.com/posts/1",
        "https://jsonplaceholder.typicode.com/posts/2",
        "https://jsonplaceholder.typicode.com/users/1",
    ]

    ok = wait_until_ready(urls[0])

    if not ok:
        print("Service not ready, but continue anyway...")

    results = batch_fetch(urls, mode="bot")

    print_summary(results)

    info = fetch_and_verify(urls[0], delay=0.2)

    print("Verify result:", info)
