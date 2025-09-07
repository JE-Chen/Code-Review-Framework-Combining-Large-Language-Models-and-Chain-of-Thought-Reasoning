**GitHub PR Summary**

**Issue #:** Not specified

**Description:** The author of this PR is changing the default thread pool implementation in `AwsAsyncClientBuilder` to prevent unnecessary thread occupancy and memory leaks.

**Problem:** The author experienced a memory leak when using a fixed thread pool to transmit large amounts of data to SQS.

**Solution:** The author is replacing the fixed thread pool with a `ThreadPoolExecutor` that uses a `LinkedBlockingQueue` to manage tasks. This change allows the thread pool to dynamically adjust its size based on the number of available threads.

**Code Change:**

```java
private ExecutorService defaultExecutor() {
    return new ThreadPoolExecutor(0, getClientConfiguration().getMaxConnections(), 60L, TimeUnit.SECONDS, new LinkedBlockingQueue<Runnable>());
}
```

**License:** The author confirms that the contribution can be used, modified, copied, and redistributed under the terms of the contributor's choice.