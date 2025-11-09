Here's a concise summary of the GitHub PR:

### **Problem**
- The existing `defaultExecutor()` implementation used `Executors.newFixedThreadPool()`, which **creates a fixed number of threads upfront** (equal to `getClientConfiguration().getMaxConnections()`).
- This caused **unnecessary thread occupancy and memory leaks** in scenarios involving large data transfers (e.g., to SQS), as threads weren’t released after use, leading to resource exhaustion.

### **Solution**
- Replaced `newFixedThreadPool()` with a **custom `ThreadPoolExecutor`** configured as:
  ```java
  new ThreadPoolExecutor(
      0,                          // Core pool size = 0 (threads created only when needed)
      getClientConfiguration().getMaxConnections(), // Max pool size
      60L, TimeUnit.SECONDS,      // Idle timeout (threads terminated after 60s of inactivity)
      new LinkedBlockingQueue<Runnable>()
  )
  ```
- **Key improvements**:
  1. **Dynamic thread creation**: Threads are only created when tasks arrive (avoids upfront thread allocation).
  2. **Automatic cleanup**: Idle threads are terminated after 60 seconds, preventing memory leaks.
  3. **Preserves max connection limit**: Ensures no more than `maxConnections` threads run concurrently.

### **Impact**
- Fixes the memory leak issue observed in large data transfers (e.g., SQS).
- Maintains the same max concurrency behavior while optimizing resource usage.
- Applies to **all AWS async clients** using `AwsAsyncClientBuilder`.

> **Why this matters**: The old implementation held threads indefinitely, while the new one efficiently reuses threads and releases them when idle, eliminating the memory leak.