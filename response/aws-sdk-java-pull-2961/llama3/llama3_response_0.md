**Pull Request Summary**

**Issue #:** Not provided

**Description:** The author is proposing a change to the default thread pool implementation in `AwsAsyncClientBuilder` to prevent unnecessary thread occupancy and memory leaks.

**Problem Statement:** The author experienced a memory leak when using a fixed thread pool to transmit large amounts of data to SQS.

**Change:** The author suggests replacing the fixed thread pool with a `ThreadPoolExecutor` with the following settings:

* Core pool size: 0 (allowing the pool to dynamically adjust to the number of threads needed)
* Maximum pool size: `getClientConfiguration().getMaxConnections()`
* Keep-alive time: 60 seconds
* Queue: `LinkedBlockingQueue<Runnable>`

**Code Change:**

```java
private ExecutorService defaultExecutor() {
    return new ThreadPoolExecutor(0, getClientConfiguration().getMaxConnections(), 60L, TimeUnit.SECONDS, new LinkedBlockingQueue<Runnable>());
}
```

**Confirmation:** The author confirms that they grant the maintainers of the project permission to use, modify, copy, and redistribute their contribution under the terms of the project's choice.