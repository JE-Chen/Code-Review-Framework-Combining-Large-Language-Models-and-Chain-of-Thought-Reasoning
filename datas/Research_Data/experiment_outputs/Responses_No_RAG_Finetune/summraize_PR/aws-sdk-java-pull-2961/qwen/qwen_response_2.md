Here's a concise summary of the GitHub PR:

**Problem**:  
The default `fixedThreadPool` implementation in `AwsAsyncClientBuilder` caused **memory leaks and unnecessary thread occupancy** when handling large data transfers (e.g., to SQS). Fixed thread pools never released threads after use, leading to resource bloat.

**Fix**:  
Replaced `Executors.newFixedThreadPool()` with a **dynamic thread pool** using `ThreadPoolExecutor` configured as:  
```java
new ThreadPoolExecutor(
    0,                          // Core threads = 0 (no threads created upfront)
    getClientConfiguration().getMaxConnections(), // Max threads
    60L, TimeUnit.SECONDS,      // Threads idle for 60s before termination
    new LinkedBlockingQueue<Runnable>()
)
```

**Key Improvements**:  
1. **No upfront thread allocation** (core threads = 0) → Reduces memory overhead.  
2. **Threads released after inactivity** (60s keep-alive) → Prevents memory leaks.  
3. **Safely scales** to `maxConnections` but avoids holding unused threads.  

**Impact**:  
Resolves memory leaks in long-running async operations (e.g., large SQS payloads) by allowing threads to be reclaimed when idle. The change affects all SDK users of `AwsAsyncClientBuilder` by default.  

> 💡 **Why this works**: The old fixed pool *always kept all threads alive*, while the new pool *dynamically creates/terminates threads* based on demand, aligning with best practices for async resource management.