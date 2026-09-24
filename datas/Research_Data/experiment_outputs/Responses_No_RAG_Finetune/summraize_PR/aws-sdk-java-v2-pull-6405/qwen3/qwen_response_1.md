Here's a concise summary of the GitHub PR:

### 🛠️ **Core Problem Fixed**
The SDK failed to propagate **file modification errors** during async uploads (e.g., S3 `putObject`), leading to silent corruption. Previously:
1. Errors were **not surfaced** (checked too late in `onComplete` after Netty canceled the subscription).
2. Errors were `IOException` (retryable by default), but file changes should be **terminal**.
3. File metadata (size/modification time) was checked *once per request*, missing changes between retries/splits.

---

### ✅ **Key Fixes**
1. **Validation Timing**  
   - Moved file integrity check **before** `signalOnNext` (ensures error is signaled *before* Netty cancels the subscription).
2. **Exception Type**  
   - Changed from `IOException` → `SdkClientException` (non-retryable, matches SDK error semantics).
3. **Metadata Capture**  
   - Captured `modifiedTimeAtStart` and `sizeAtStart` **at request construction** (not per retry/split), ensuring consistent checks.

---

### 🧪 **Testing & Behavior**
- **New Tests Added**: Covers file size/modification changes during upload.
- **Behavior Changes**:
  - ✅ **S3AsyncClient (Netty/CRT)**: Now throws `SdkClientException` (e.g., `"File last-modified time changed..."`).
  - ✅ **TransferManager (Java)**: Throws new exception.
  - ❌ **S3CrtAsyncClient/TransferManager (CRT)**: Unchanged (already handled correctly).
- **Exception Example**:
  ```java
  SdkClientException: File last-modified time changed... 
  Initial: 2025-09-05T19:20:46.540910708Z 
  Current: 2025-09-05T19:20:47.981202736Z
  ```

---

### 📝 **Why This Matters**
- Prevents **silent data corruption** (e.g., if a file is modified mid-upload, the SDK now fails fast).
- Ensures **consistent error handling** across all clients (except CRT, which already worked correctly).
- Fixes a critical bug where users couldn’t detect file changes during async operations.

---

### 🔑 **Summary in One Sentence**
> This PR ensures file modification errors during async uploads are **properly surfaced as non-retryable exceptions** by moving validation logic earlier and capturing metadata at request start, fixing silent corruption risks.