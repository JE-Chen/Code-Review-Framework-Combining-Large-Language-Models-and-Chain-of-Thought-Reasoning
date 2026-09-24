Here's a concise summary of the GitHub PR:

---

### **Problem Fixed**  
File modification errors during async uploads (e.g., `S3AsyncClient`) were **not propagated** to the user, causing silent failures. Three specific issues were addressed:  
1. **Errors swallowed** – File change checks ran *after* Netty canceled the subscription (per Reactive Streams spec), so errors never reached the caller.  
2. **Retryable errors** – Original `IOException` was treated as retryable (wrong for file changes).  
3. **Missing detection** – File metadata (size/mod time) was checked *per-part* (e.g., in multipart uploads), so changes between parts went undetected.

---

### **Key Fixes**  
1. **Validation moved** – Checks for file size/mod time **before** sending the last bytes to Netty (ensuring errors are signaled *before* cancellation).  
2. **Exception type changed** – From `IOException` to `SdkClientException` (non-retryable, terminal error).  
3. **Metadata captured at start** – `modifiedTimeAtStart` and `sizeAtStart` are set *once* when the request begins (not per-part), ensuring consistent checks across retries/splits.  

---

### **Result**  
- **All async clients (Netty-based)** now **throw `SdkClientException`** with clear error messages (e.g., `"File last-modified time changed after reading started"`).  
- **CRT-based clients** (e.g., `S3CrtAsyncClient`, `CrtTM`) **remain unaffected** (they handle file changes differently).  
- **Tests added** to cover:  
  - File size changes (too short/long)  
  - File modification time changes  
  - File deletion  
  - Split multipart uploads  

---

### **Example Error**  
```java
SdkClientException: 
  Unable to execute HTTP request: File last-modified time changed after reading started. 
  Initial modification time: 2025-09-05T19:20:46.540910708Z. 
  Current modification time: 2025-09-05T19:20:47.981202736Z
```

---

### **Why It Matters**  
- **User impact**: Prevents silent data corruption (e.g., partial uploads due to file changes).  
- **Correct behavior**: File changes are now treated as **terminal errors** (not retryable).  
- **Backward-compatible**: Only changes error handling (no breaking changes to API).  

> ✅ **Type**: Bug fix (non-breaking)  
> ✅ **Testing**: Verified across all async clients (Netty-based), CRT clients unchanged.  
> ✅ **Changelog**: Added as a bug fix entry.  

--- 

**In short**: Files modified *during* an upload now immediately fail with a clear, non-retryable error.