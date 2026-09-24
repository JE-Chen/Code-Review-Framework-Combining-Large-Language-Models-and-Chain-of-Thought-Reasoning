Here's a concise summary of the GitHub PR:

---

### **Issue**  
The default `fixedThreadPool` implementation in `AwsAsyncClientBuilder` caused **memory leaks and unnecessary thread occupancy** when handling large data transfers (e.g., to SQS). Threads failed to terminate after processing, leading to resource exhaustion.

### **Fix**  
Replaced `Executors.newFixedThreadPool()` with a **dynamic thread pool** using `ThreadPoolExecutor` configured as:  
```java
new ThreadPoolExecutor(
    0,                          // Core pool size (0 threads initially)
    getClientConfiguration().getMaxConnections(), // Max threads
    60L, TimeUnit.SECONDS,      // Idle timeout (threads terminate after 60s of inactivity)
    new LinkedBlockingQueue<Runnable>() // Unbounded queue
)
```

### **Why This Solves the Problem**  
- **Prevents memory leaks**: Threads are **terminated after inactivity** (vs. fixed pool where threads *always* stay alive).  
- **Optimizes resource usage**: Pool grows *only* when needed (up to `maxConnections`), avoiding unnecessary thread creation.  
- **Safe for large payloads**: Handles bursty workloads (e.g., large SQS messages) without leaking threads.

### **Impact**  
- **Default behavior changes** for all `AwsAsyncClientBuilder` users.  
- **No code changes required** for SDK consumers (fix applies automatically).  
- Addresses the root cause: Fixed pools are unsuitable for async clients where thread demand varies.

> ℹ️ *Note: The `LinkedBlockingQueue` is unbounded, but the max thread count (`getMaxConnections()`) prevents runaway thread creation.*