Here's a concise summary of the GitHub PR:

**Problem:**  
The current default thread pool (`Executors.newFixedThreadPool()`) in `AwsAsyncClientBuilder` causes **memory leaks and unnecessary thread occupancy** when handling large data transfers (e.g., to SQS). Fixed thread pools retain all threads indefinitely, even after requests complete, leading to resource exhaustion.

**Solution:**  
Replace the default thread pool with a **configurable `ThreadPoolExecutor`** that:
- Starts with **0 core threads** (threads are created only when needed).
- Uses `maxConnections` as the **maximum thread count**.
- Allows threads to **terminate after 60 seconds of inactivity** (via `keepAliveTime`).
- Uses an **unbounded `LinkedBlockingQueue`** for task management.

**Code Change:**  
```java
// Before (causes leaks)
return Executors.newFixedThreadPool(getClientConfiguration().getMaxConnections());

// After (fixes leaks)
return new ThreadPoolExecutor(0, getClientConfiguration().getMaxConnections(), 
                            60L, TimeUnit.SECONDS, 
                            new LinkedBlockingQueue<Runnable>());
```

**Key Impact:**  
- Prevents memory leaks by **releasing idle threads** after 60 seconds.
- Reduces unnecessary thread occupancy (threads are only created for active work).
- Maintains the same `maxConnections` limit for concurrency control.

**Why This Matters:**  
Fixes a critical resource leak scenario (e.g., large SQS payloads) where threads were never released, ensuring the SDK scales safely under heavy load. The change is **backward-compatible** (uses existing config values) and aligns with best practices for thread pool management.