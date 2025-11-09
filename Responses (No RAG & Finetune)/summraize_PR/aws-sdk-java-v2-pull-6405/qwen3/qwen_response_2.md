Here's a concise summary of the GitHub PR:

### **Core Problem**
File modification errors during async file uploads (e.g., S3 `putObject`) were **not properly surfaced** to users. The SDK detected file changes (size/modification time) but failed to propagate errors due to:
1. Validation logic ran *after* Netty canceled the subscription (per Reactive Streams spec), so errors were ignored.
2. Errors were `IOException` (retryable by default), but file changes should be **terminal** (non-retryable).
3. File metadata (size/mod time) was re-checked per retry/split, missing changes *between* attempts.

---

### **Key Fixes**
1. **Validation Timing**  
   Moved file metadata checks **before** signaling the last bytes to Netty (ensures errors are raised *before* subscription cancellation).

2. **Exception Type**  
   Changed from `IOException` → `SdkClientException` (non-retryable, terminal error).

3. **Consistent Metadata**  
   Captured `modifiedTimeAtStart`/`sizeAtStart` **once at request creation** (not per retry/split), ensuring consistent checks.

---

### **Behavior Changes**
| Scenario                          | Before (Broken)       | After (Fixed)               |
|-----------------------------------|-----------------------|-----------------------------|
| File modified mid-upload          | Silent failure        | Throws `SdkClientException` |
| Example error message             | `IOException` (retryable) | `File last-modified time changed...` (terminal) |
| S3AsyncClient (Netty/CRT)         | No exception          | Throws new exception        |
| TransferManager (Java/CRT)        | No exception          | Throws new exception        |
| CRT clients (S3CrtAsyncClient)    | Unchanged (no error)  | Unchanged (no error)        |

---

### **Testing**
- Added 4 new tests covering:
  - File size change (too short/long)
  - File modification time change
  - Split uploads (multi-part) with file change mid-upload
- Verified behavior across all SDK clients (S3AsyncClient, CRT, TransferManager).

---

### **Why This Matters**
- Prevents **silent data corruption** (e.g., partial uploads with modified files).
- Ensures users **immediately see** file modification errors (not buried in retries).
- Fixes critical race condition in async file handling.

> 💡 **Key Takeaway**: File changes during upload are now **terminal errors** (not retryable), with clear diagnostics (e.g., `Initial modification time: 2025-09-05T19:20:46.540910708Z. Current time: 2025-09-05T19:20:47.981202736Z`).

*PR Type: Bug fix (non-breaking, adds terminal error handling for file changes).*