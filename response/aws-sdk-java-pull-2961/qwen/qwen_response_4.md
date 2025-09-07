Here's a concise summary of the GitHub PR:

**Problem:**  
The default `fixedThreadPool` (via `Executors.newFixedThreadPool()`) in `AwsAsyncClientBuilder` caused **unnecessary thread occupancy and memory leaks** when processing large data payloads (e.g., to SQS). Threads weren't released after work completed, leading to resource exhaustion.

**Fix:**  
Replaced the default thread pool implementation with a **dynamic `ThreadPoolExecutor`** that:
- Starts with **0 core threads** (scales up only when needed).
- Uses a **`LinkedBlockingQueue`** (unbounded, safe for most use cases).
- Sets **60-second keep-alive** for idle threads.
- Limits max threads to `getClientConfiguration().getMaxConnections()`.

**Code Change:**  
```java
// BEFORE (caused leaks)
// return Executors.newFixedThreadPool(getClientConfiguration().getMaxConnections());

// AFTER (fixes leaks)
return new ThreadPoolExecutor(
    0, 
    getClientConfiguration().getMaxConnections(), 
    60L, 
    TimeUnit.SECONDS, 
    new LinkedBlockingQueue<Runnable>()
);
```

**Impact:**  
- Prevents memory leaks by allowing threads to terminate after inactivity.
- Optimizes thread usage (no idle threads lingering after work).
- Maintains connection limits via `maxConnections` config.

**Why it matters:**  
The old fixed pool *always* kept all threads alive, even when idle. The new pool *releases idle threads after 60 seconds*, aligning with typical async client behavior and avoiding resource leaks. This is critical for long-running applications handling variable workloads (e.g., large SQS payloads).  

*(PR resolves memory leak in default async client configuration.)*