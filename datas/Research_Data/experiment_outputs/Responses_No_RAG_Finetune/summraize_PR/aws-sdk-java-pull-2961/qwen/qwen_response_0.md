Here's a concise summary of the GitHub PR:

**Problem**:  
The default `fixedThreadPool` (via `Executors.newFixedThreadPool()`) in `AwsAsyncClientBuilder` caused **unnecessary thread occupancy and memory leaks** when processing large data transfers (e.g., to SQS). Threads were not terminating after operations, leading to resource exhaustion.

**Fix**:  
Replaced the default thread pool implementation with a **dynamic `ThreadPoolExecutor`** that:
- Starts with **0 core threads** (threads created only when needed).
- Uses **`maxConnections`** as the maximum thread count (preserving existing concurrency limits).
- Allows idle threads to **timeout after 60 seconds** (preventing leak).
- Uses an **unbounded `LinkedBlockingQueue`** for task queuing.

**Code Change**:  
```java
// Old (problematic):
// return Executors.newFixedThreadPool(getClientConfiguration().getMaxConnections());

// New (fixed):
return new ThreadPoolExecutor(
    0, 
    getClientConfiguration().getMaxConnections(), 
    60L, TimeUnit.SECONDS, 
    new LinkedBlockingQueue<Runnable>()
);
```

**Impact**:  
- Eliminates memory leaks by **releasing idle threads** after 60 seconds.  
- Maintains the same **maximum concurrency limit** (`maxConnections`).  
- Prevents thread leaks during large data operations (e.g., SQS sends).  

**Why it matters**:  
This change ensures threads are **only active when needed**, resolving the memory leak issue while preserving the SDK’s intended concurrency behavior. The fix is applied globally to all `AwsAsyncClientBuilder` instances.