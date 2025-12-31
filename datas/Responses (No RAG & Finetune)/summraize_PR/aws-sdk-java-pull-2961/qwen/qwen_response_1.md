Here's a concise summary of the GitHub PR:

**Problem:**  
The default `fixedThreadPool` in `AwsAsyncClientBuilder` caused **unnecessary thread occupancy and memory leaks** when processing large data transfers (e.g., to SQS). Fixed thread pools never release threads, leading to resource exhaustion.

**Fix:**  
Replaced `Executors.newFixedThreadPool()` with a **dynamic `ThreadPoolExecutor`** configured as:  
```java
new ThreadPoolExecutor(
    0,                          // Core pool size (start empty)
    getClientConfiguration().getMaxConnections(), // Max threads
    60L, TimeUnit.SECONDS,      // Thread timeout (idle threads terminate after 60s)
    new LinkedBlockingQueue<Runnable>() // Task queue
)
```

**Key Benefits:**  
✅ **Prevents memory leaks** by allowing idle threads to terminate after 60 seconds.  
✅ Maintains max connection limits via `getMaxConnections()`.  
✅ Solves the specific issue where threads weren’t releasing after large SQS operations.  

**Why it matters:**  
The change ensures threads are only created when needed and released after inactivity, avoiding the resource leak observed in the original implementation. No behavioral changes to connection limits—only fixes the leak.  

*(PR author confirms contribution terms compliance.)*