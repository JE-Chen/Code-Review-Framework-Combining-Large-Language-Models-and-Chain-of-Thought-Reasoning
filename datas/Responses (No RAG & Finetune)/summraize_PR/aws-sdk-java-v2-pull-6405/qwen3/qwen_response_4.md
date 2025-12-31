Here's a concise summary of the GitHub PR:

### 🛠️ **Core Fix**
Addresses **three critical issues** with file modification detection in `FileAsyncRequestBody` (used for S3 uploads):
1. **Unpropagated errors**: Exceptions when file changes were detected were silently swallowed (never reached the SDK user).
2. **Retryable exceptions**: File-modification errors were `IOException` (retryable by default), but should be **terminal** (non-retryable).
3. **Missed modifications**: File changes *between retries/splits* weren't detected (initial file state was captured per execution, not globally).

### 🔧 **Key Changes**
| Component | Change | Purpose |
|-----------|--------|---------|
| `FileAsyncRequestBody` | Added `modifiedTimeAtStart`/`sizeAtStart` fields | Capture *consistent* initial file state (across retries/splits). |
| `FileSubscription` | Moved validation **before** `signalOnNext` | Ensures errors are signaled *before* Netty cancels subscription (per Reactive Streams spec). |
| Exception type | Changed from `IOException` → `SdkClientException` | Makes errors **non-retryable** (correct behavior for file changes). |
| `FileAsyncRequestBody` builder | Added `.modifiedTimeAtStart()`/`.sizeAtStart()` | Enables consistent initial state for split/retry scenarios. |

### ✅ **Testing & Behavior**
- **New tests added**: Covers file size/modification changes during read, split uploads, and preset initial states.
- **Manual testing results**:
  - ✅ **All non-CRT clients** (S3AsyncClient, TransferManager) now **throw `SdkClientException`** on file change.
  - ❌ **CRT clients** (S3CrtAsyncClient, CrtTM) unchanged (they handle file state differently).
- **Example exception**:
  ```java
  SdkClientException: File last-modified time changed after reading started. 
  Initial: 2025-09-05T19:20:46.540Z, Current: 2025-09-05T19:20:47.981Z
  ```

### 📝 **Why This Matters**
- Prevents silent data corruption (e.g., partial uploads due to file changes).
- Ensures users get **immediate, non-retryable errors** when files are modified mid-upload.
- Fixes a critical race condition where Netty would cancel the subscription *before* errors were signaled.

### 📦 **Impact**
- **Bug fix** (non-breaking change).
- Affects all SDK clients using `FileAsyncRequestBody` (S3, TransferManager) **except CRT clients**.
- Fixes a long-standing edge case in multi-part uploads and retries.

> 💡 **Key Insight**: The fix moves validation from `onComplete` (too late) to *during byte reads* (before subscription cancellation), ensuring errors are propagated correctly. The exception type change ensures users aren't accidentally retrying corrupted uploads.