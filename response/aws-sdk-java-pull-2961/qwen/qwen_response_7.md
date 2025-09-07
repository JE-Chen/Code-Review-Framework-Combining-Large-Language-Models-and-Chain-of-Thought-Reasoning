Here's a concise summary of the GitHub PR:

**Problem:**  
The default `fixedThreadPool` (via `Executors.newFixedThreadPool()`) in `AwsAsyncClientBuilder` caused **unnecessary thread occupancy and memory leaks** when processing large data transfers (e.g., to SQS). Threads never terminated after use, leading to resource exhaustion.

**Solution:**  
Replace the default thread pool with a **dynamic `ThreadPoolExecutor`** that:
- Starts with **0 core threads** (threads only created when needed).
- Uses `maxConnections` as the **maximum thread limit**.
- Allows idle threads to **terminate after 60 seconds** (via `keepAliveTime`).
- Uses a `LinkedBlockingQueue` for task management.

**Key Code Change:**
```java
// Old (problematic):
// return Executors.newFixedThreadPool(getClientConfiguration().getMaxConnections());

// New (fixed):
return new ThreadPoolExecutor(
    0, 
    getClientConfiguration().getMaxConnections(), 
    60L, 
    TimeUnit.SECONDS, 
    new LinkedBlockingQueue<Runnable>()
);
```

**Why It Fixes the Issue:**  
The new pool avoids holding unused threads indefinitely (unlike `fixedThreadPool`), preventing memory leaks and reducing overhead for long-running applications. Threads now **terminate after 60 seconds of inactivity**, freeing resources.

**Impact:**  
Addresses memory leaks in scenarios with large data transfers (e.g., SQS), improving resource efficiency without changing user-configurable behavior.  
*Note: This is a behavioral change to the default implementation only (user-configured pools remain unaffected).*