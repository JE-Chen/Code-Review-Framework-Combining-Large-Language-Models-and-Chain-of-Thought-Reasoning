Here's a concise summary of the GitHub PR:

### 🛠️ **Problem**
- The default `fixedThreadPool` (via `Executors.newFixedThreadPool()`) in `AwsAsyncClientBuilder` causes **unnecessary thread occupancy** and **memory leaks** when processing large data volumes (e.g., to SQS).
- Threads remain allocated indefinitely after operations complete, leading to memory bloat.

### ✅ **Solution**
Replaced the default thread pool implementation with a **dynamic `ThreadPoolExecutor`** that:
- Starts with **0 core threads** (avoids upfront thread allocation).
- Scales up to `getClientConfiguration().getMaxConnections()` threads.
- **Reclaims idle threads after 60 seconds** (via `keepAliveTime`).
- Uses a `LinkedBlockingQueue` for task management.

### 🔑 **Key Code Change**
```java
// Before (causes memory leak):
// return Executors.newFixedThreadPool(getClientConfiguration().getMaxConnections());

// After (fixes leak):
return new ThreadPoolExecutor(
    0,                          // corePoolSize (start with 0 threads)
    getClientConfiguration().getMaxConnections(), // maxPoolSize
    60L, TimeUnit.SECONDS,      // keep-alive time
    new LinkedBlockingQueue<Runnable>()
);
```

### 💡 **Why It Works**
- **No upfront threads**: Threads are created only when needed (reduces memory usage).
- **Idle thread cleanup**: Threads terminate after 60s of inactivity (prevents leaks).
- **Safe scaling**: Max threads still capped at `maxConnections` (avoids over-provisioning).

### ⚙️ **Impact**
- Resolves memory leaks in high-volume scenarios (e.g., large SQS data transfers).
- Maintains the same max thread limit but with **dynamic resource usage**.
- Backward-compatible (no API changes).

> **In short**: This PR swaps a leak-prone fixed pool for a smarter, self-cleaning thread pool that scales efficiently and avoids memory bloat. 🚫MemoryWarning