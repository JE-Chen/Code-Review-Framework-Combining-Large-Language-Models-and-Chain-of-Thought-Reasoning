# 一個「功能正常」的 API Client 程式（requests 版 v2）
# 但 HTTP / Header / Cache / Stream / API 設計全面翻車 🤮

import requests
import time
import hashlib


# ❌ Mutable Default Argument：headers 當預設參數，經典地雷
def fetch_resource(url, headers={}, use_cache=True, allow_redirect=True):
    # ❌ Function Attribute 當快取（Hidden State in Function Object）
    if not hasattr(fetch_resource, "cache"):
        fetch_resource.cache = {}

    # ❌ Cache Key 設計錯誤：只用 URL，忽略 headers / query
    cache_key = url

    if use_cache and cache_key in fetch_resource.cache:
        # ❌ 回傳舊 Response 物件（Stale Object Reuse）
        return fetch_resource.cache[cache_key]

    # ❌ 在 function 內偷偷修改傳入參數（Side-effect on Arguments）
    headers["User-Agent"] = "BadClient/1.0"

    # ❌ allow_redirects 當參數傳來傳去（Leaky Abstraction）
    r = requests.get(
        url,
        headers=headers,
        allow_redirects=allow_redirect
    )

    # ❌ Cache HTTP Response Object 本身（Unsafe Object Caching）
    if use_cache:
        fetch_resource.cache[cache_key] = r

    return r


# ❌ Shadowing Built-in Name（命名成 hash）
def hash(text):
    # ❌ 自己重造輪子（Reinventing the Wheel）
    h = hashlib.md5()
    h.update(text.encode("utf-8"))
    return h.hexdigest()


# ❌ Confusing API：參數名與實際用途不符
def download_file(url, path, preview=False, verbose=False):
    # ❌ stream=True 但沒有正確關閉 response（Resource Leak）
    resp = requests.get(url, stream=True)

    # ❌ Verbose flag 污染核心流程
    if verbose:
        print("Status:", resp.status_code)
        print("Headers:", resp.headers)

    content = b""

    # ❌ Magic Chunk Size
    for chunk in resp.iter_content(chunk_size=1234):
        # ❌ 假裝支援 preview，其實還是全抓
        if preview and len(content) > 3000:
            break
        content += chunk

    # ❌ 不檢查 Content-Type 就直接存檔
    with open(path, "wb") as f:
        f.write(content)

    return path


# ❌ Overloaded Function：又打 API、又 parse header、又算 checksum、又 sleep
def fetch_and_verify(url, delay=0.0):
    r = fetch_resource(url)

    # ❌ Logging Sensitive Headers（資安臭味）
    print("Request headers:", r.request.headers)

    # ❌ 直接信任 encoding
    text = r.text

    # ❌ 用自製 hash 來當驗證機制（Weak Home-grown Security）
    checksum = hash(text)

    # ❌ Artificial Delay：毫無理由 sleep
    if delay > 0:
        time.sleep(delay)

    return {
        "url": url,
        "length": len(text),
        "checksum": checksum
    }


# ❌ Header State Machine Smell：用 dict 當流程控制
def batch_fetch(urls, mode="normal"):
    results = []

    headers = {}

    # ❌ mode 用字串控制多種邏輯（Stringly Typed Control Flow）
    if mode == "mobile":
        headers["User-Agent"] = "iPhone"
    elif mode == "bot":
        headers["User-Agent"] = "GoogleBot"
    else:
        headers["User-Agent"] = "Desktop"

    for u in urls:
        # ❌ 每次都共用同一份 headers（Cross-request Contamination）
        r = fetch_resource(u, headers=headers, use_cache=True)

        # ❌ Redirect Policy 混在商業邏輯中
        if r.history:
            print("Redirected:", u, "->", r.url)

        # ❌ Tight Coupling to Header Format
        server = r.headers.get("Server", "unknown")

        results.append({
            "url": u,
            "status": r.status_code,
            "server": server,
            "size": len(r.content)
        })

    return results


# ❌ Polling API 反模式：固定間隔一直打
def wait_until_ready(url, max_try=5):
    tries = 0

    while tries < max_try:
        r = fetch_resource(url, use_cache=False)

        # ❌ Magic Status Code Rule
        if r.status_code == 200:
            return True

        # ❌ Fixed Sleep Without Backoff
        time.sleep(1)
        tries += 1

    return False


# ❌ Output-only Function：完全無回傳值
def print_summary(results):
    print("=== FETCH SUMMARY ===")

    for r in results:
        # ❌ Inconsistent Field Order / Format
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

    # ❌ 明明可以回傳資料卻選擇只印
    return None


# 主流程
def main():
    urls = [
        "https://jsonplaceholder.typicode.com/posts/1",
        "https://jsonplaceholder.typicode.com/posts/2",
        "https://jsonplaceholder.typicode.com/users/1",
    ]

    # ❌ Temporal Coupling：一定要先 wait 才 batch
    ok = wait_until_ready(urls[0])

    if not ok:
        print("Service not ready, but continue anyway...")

    results = batch_fetch(urls, mode="bot")

    print_summary(results)

    # ❌ 同一 URL 重複打，但 cache 規則錯誤可能回舊資料
    info = fetch_and_verify(urls[0], delay=0.2)

    print("Verify result:", info)
