Here's a concise summary of the GitHub PR:

**Problem:**  
The default `fixedThreadPool` implementation in `AwsAsyncClientBuilder` caused **unnecessary thread occupancy and memory leaks** (e.g., threads not terminating after large SQS data transfers, leading to memory bloat).

**Solution:**  
Replace `Executors.newFixedThreadPool()` with a **configurable `ThreadPoolExecutor`** that:
- Starts with **0 core threads** (creates threads only when needed).
- Uses `maxConnections` as the **maximum pool size**.
- Allows idle threads to **terminate after 60 seconds** (`60L, TimeUnit.SECONDS`).
- Uses `LinkedBlockingQueue` for task queuing.

**Key Code Change:**
```java
// Before (caused leaks):
// return Executors.newFixedThreadPool(getClientConfiguration().getMaxConnections());

// After (fixes leaks):
return new ThreadPoolExecutor(
    0, 
    getClientConfiguration().getMaxConnections(), 
    60L, 
    TimeUnit.SECONDS, 
    new LinkedBlockingQueue<Runnable>()
);
```

**Why This Fixes the Issue:**  
- Threads are **not pre-created** (avoids unnecessary occupancy).  
- Idle threads **relinquish resources after 60 seconds** (prevents memory leaks).  
- Maintains the same `maxConnections` limit for concurrency.  

**Impact:**  
Prevents memory leaks in async AWS clients (e.g., SQS) by ensuring threads are properly cleaned up after use. The change is **backward-compatible** (retains the same max connection behavior while fixing the leak).  

*Note: The PR addresses a critical resource leak in the SDK’s default async configuration.*